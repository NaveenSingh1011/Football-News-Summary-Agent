import html
import re
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor

from langchain_groq import ChatGroq

from config import MODELS_TO_TRY

# ==========================================================
# CONVERT PUBLISHED DATE TO INDIAN STANDARD TIME
# ==========================================================

def format_published_ist(timestamp):

    if not timestamp:
        return "Unknown"

    try:
        dt = datetime.fromisoformat(
            str(timestamp).strip().replace("Z", "+00:00")
        )

        # Assume UTC if the timestamp has no timezone information
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        # Convert to Indian Standard Time
        ist_time = dt.astimezone(
            ZoneInfo("Asia/Kolkata")
        )

        # Format with a space between date and time
        return ist_time.strftime(
            "%Y-%m-%d %H:%M:%S IST"
        )

    except (ValueError, TypeError):
        return str(timestamp)


_llm_cache = {}


def get_llm(model):
    if model not in _llm_cache:
        _llm_cache[model] = ChatGroq(model=model, temperature=0.1, max_tokens=1500)
    return _llm_cache[model]


SUMMARY_SYSTEM = """
You are a careful, knowledgeable football journalist.

Summarize the supplied article for football fans.

Rules:
- Use only facts in the supplied material.
- Never invent transfers, scores, injuries, quotes or statistics.
- Clearly distinguish rumours from confirmed developments.
- Do not add unrelated clubs or players.
- Do not confuse American football with association football.
- Explain the main development and why it matters, only when supported by the source.
- Aim for 100-160 words for a substantial article. Be shorter when text is limited.
- Return only the summary.
"""


def clean_html(text):
    text = html.unescape(str(text or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def llm_summary(system, user):
    """Call Groq. Retries on rate limits, then falls back to other models."""
    last_error = None
    for model in MODELS_TO_TRY:
        for attempt in range(3):
            try:
                reply = get_llm(model).invoke([("system", system), ("human", user)])
                text = str(reply.content or "").strip()
                if text:
                    return text, model
                last_error = "empty response"
                break
            except Exception as error:
                last_error = error
                if "429" in str(error) or "rate" in str(error).lower():
                    time.sleep(5 * (attempt + 1))
                    continue
                break
    raise RuntimeError(f"all models failed: {last_error}")




def summarize_one(article):
    """Summarize one article. Runs in parallel with the others."""
    title = str(article.get("title") or "Untitled")
    source = str(article.get("source") or "Unknown")

    # Convert publication timestamp to IST
    published = format_published_ist(
        article.get("published_at")
    )
    content = clean_html(article.get("content"))
    description = clean_html(article.get("description"))

    if len(content.split()) >= 60:
        material, material_type = content[:18000], "Retrieved article text"
    else:
        material = (
            f"Headline: {title}\nDescription: {description}\n"
            f"Available excerpt: {content}"
        )
        material_type = "Headline and available excerpt"

    base = {
        "title": title, "source": source, "published": published,
        "url": article.get("url") or "",
    }

    if len(material.split()) < 25:
        return {
            **base,
            "summary": "The full article could not be loaded, so a reliable summary is not possible.",
            "model": "none", "status": "no text",
            "log": f"SELF-CORRECT: no usable text for '{title[:50]}'",
        }

    user = (
        f"Headline: {title}\nPublisher: {source}\nPublished: {published}\n"
        f"Source type: {material_type}\n\nArticle text:\n{material}"
    )
    try:
        text, model = llm_summary(SUMMARY_SYSTEM, user)
        if material_type != "Retrieved article text":
            text += "\n\n**Source limitation:** Only a headline or excerpt was available."
        return {
            **base, "summary": text, "model": model, "status": "ok",
            "log": f"LLM summarized '{title[:50]}' with {model}",
        }
    except Exception as error:

        print("\n" + "=" * 60)
        print("[SUMMARIZATION ERROR]")
        print(f"[ARTICLE] {title}")
        print(f"[ERROR TYPE] {type(error).__name__}")
        print(f"[ERROR DETAILS] {error}")
        print("=" * 60 + "\n")

        return {
            **base,
            "summary": "Summary generation failed. Please check the terminal.",
            "model": "none",
            "status": "failed",
            "log": f"Summary failed: {type(error).__name__}",
        }


def summarize_node(state):
    """Summarize all articles at the same time instead of one by one."""
    articles = state["articles"]
    if not articles:
        return {"summaries": [], "trace": ["SUMMARIZE: no articles to summarize"]}

    with ThreadPoolExecutor(max_workers=min(5, len(articles))) as pool:
        results = list(pool.map(summarize_one, articles))

    logs = [r.pop("log") for r in results]
    return {"summaries": results, "trace": logs}


