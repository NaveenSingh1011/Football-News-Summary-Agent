import operator
from concurrent.futures import ThreadPoolExecutor
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, END

from query_parser import parse_query, score_article
from news_tools import search_news, fetch_full_article, canonical_url, is_duplicate
from summarizer import summarize_node


class NewsState(TypedDict):
    query: str
    limit: int
    parsed: dict
    attempt: int
    candidates: list
    relevant: list
    relaxed: bool
    articles: list
    summaries: list
    report: str
    trace: Annotated[list, operator.add]   # every node appends log lines




def broadened_queries(parsed, attempt):
    """Search variants used on retries (self-correction)."""
    who = " ".join(e.title() for e in parsed["entities"])
    if attempt == 2 and who:
        return [who, f"{who} news", f"{who} latest"]
    return ["football news", "premier league news", "latest football transfer news"]


# 7. AGENT NODES
# ==========================================================

def plan_node(state):
    parsed = parse_query(state["query"])
    return {
        "parsed": parsed,
        "attempt": 1,
        "trace": [
            f"PLAN: clubs/players={parsed['entities'] or '-'} "
            f"topics={parsed['topics'] or '-'} keywords={parsed['extra'] or '-'}",
            f"PLAN: search queries {parsed['api_queries']}",
        ],
    }


def search_node(state):
    parsed = state["parsed"]
    if state["attempt"] == 1:
        queries = parsed["api_queries"]
    else:
        queries = broadened_queries(parsed, state["attempt"])

    candidates, seen, logs = [], set(), []
    for q in queries[:8]:
        try:
            articles = search_news.invoke({"query": q, "limit": 10})
            logs.append(f"TOOL search_news('{q}') -> {len(articles)} articles")
        except Exception as error:
            logs.append(f"TOOL ERROR search_news('{q}'): {str(error)[:80]}")
            continue
        for article in articles:
            key = canonical_url(article["url"])
            if key not in seen:
                seen.add(key)
                candidates.append(article)

    logs.append(f"SEARCH (attempt {state['attempt']}): {len(candidates)} unique candidates")
    return {"candidates": candidates, "trace": logs}


def filter_node(state):
    parsed = state["parsed"]
    kept = list(state.get("relevant", []))
    kept_urls = {canonical_url(a["url"]) for a in kept}
    logs, relaxed = [], False

    scored = []
    for article in state["candidates"]:
        if canonical_url(article["url"]) in kept_urls:
            continue
        score = score_article(parsed, article)
        if score:
            scored.append((score, article))
        else:
            logs.append(f"FILTER rejected (off-topic): {article['title'][:70]}")

    scored.sort(key=lambda x: x[0], reverse=True)
    for _, article in scored:
        if is_duplicate(article, kept):
            logs.append(f"FILTER skipped duplicate: {article['title'][:70]}")
            continue
        kept.append(article)

    # Last resort after 3 searches: accept the latest club/player news
    if not kept and state["attempt"] >= 3:
        for article in state["candidates"]:
            if score_article(parsed, article, require_topic=False) and not is_duplicate(article, kept):
                kept.append(article)
                relaxed = True
        if relaxed:
            logs.append("SELF-CORRECT: no topic match after 3 searches, using latest club/player news")

    logs.append(f"FILTER kept {len(kept)} relevant article(s)")
    return {"relevant": kept, "relaxed": relaxed, "trace": logs}


def route_after_filter(state):
    # Self-correction loop: too few good articles -> search again with broader queries
    if len(state["relevant"]) < 2 and state["attempt"] < 3:
        return "retry"
    return "enrich"


def retry_node(state):
    return {
        "attempt": state["attempt"] + 1,
        "candidates": [],
        "trace": [
            f"SELF-CORRECT: only {len(state['relevant'])} relevant article(s), "
            f"retrying with broader queries (attempt {state['attempt'] + 1})"
        ],
    }


def enrich_node(state):
    articles = state["relevant"][: state["limit"]]

    def enrich(article):
        if len(article["content"].split()) < 100:
            try:
                text = fetch_full_article.invoke({"url": article["url"]})
                if len(text) > len(article["content"]):
                    return {**article, "content": text}
            except Exception:
                pass
        return article

    with ThreadPoolExecutor(max_workers=5) as pool:
        articles = list(pool.map(enrich, articles))

    return {
        "articles": articles,
        "trace": [f"TOOL fetch_full_article -> checked full text for {len(articles)} article(s)"],
    }




def report_node(state):
    lines = [
        "# ⚽ Football News Summary Agent",
        f"**Search:** {state['query']}  ",
        f"**Articles:** {len(state['summaries'])}",
        "",
    ]
    if state.get("relaxed"):
        lines += ["> ⚠️ No topic-specific articles were found, so these are the latest stories about this club or player.", ""]
    if not state["summaries"]:
        lines += ["## No recent articles found", "Try a simpler search, such as just the club or player name.", ""]

    for i, s in enumerate(state["summaries"], start=1):
        lines += [
            f"## {i}. {s['title']}",
            f"**Publisher:** {s['source']}  ",
            f"**Published:** {s['published']}  ",
            f"**Summary:** {s['status']} ({s['model']})",
            "",
            s["summary"],
            "",
            f"[Read original article]({s['url']})",
            "",
            "---",
            "",
        ]
    return {"report": "\n".join(lines), "trace": ["REPORT: final report compiled"]}


# ==========================================================
# 8. BUILD THE LANGGRAPH
# ==========================================================

builder = StateGraph(NewsState)
builder.add_node("plan", plan_node)
builder.add_node("search", search_node)
builder.add_node("filter", filter_node)
builder.add_node("retry", retry_node)
builder.add_node("enrich", enrich_node)
builder.add_node("summarize", summarize_node)
builder.add_node("report", report_node)

builder.set_entry_point("plan")
builder.add_edge("plan", "search")
builder.add_edge("search", "filter")
builder.add_conditional_edges("filter", route_after_filter, {"retry": "retry", "enrich": "enrich"})
builder.add_edge("retry", "search")
builder.add_edge("enrich", "summarize")
builder.add_edge("summarize", "report")
builder.add_edge("report", END)

agent = builder.compile()
print("LangGraph agent ready.")
