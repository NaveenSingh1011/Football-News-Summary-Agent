from config import client, MODEL
from query_parser import normalize


# ==========================================================
# 4. GENERAL FOOTBALL QUESTIONS (used when the input is a question)
# ==========================================================

def answer_football_question(question):
    system_prompt = """
You are a knowledgeable and friendly football journalist
and football expert.

Answer the user's football question directly and naturally.

RULES:
- Answer the actual question.
- Explain football players, clubs, competitions and rules.
- Use clear and conversational language.
- Do not invent statistics, dates, quotes or achievements.
- Do not pretend to know breaking or live news.
- For information that may have changed recently,
  explain that it needs current verification.
- Keep simple answers concise and useful.
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": str(question)},
            ],
            temperature=0.2,
            max_tokens=500,
        )
        answer = response.choices[0].message.content
        return str(answer or "Unable to generate an answer.")
    except Exception as error:
        print("Groq error:", error)
        return "Unable to answer this question right now."


NEWS_WORDS = {
    "news", "latest", "recent", "recently", "update", "updates", "today",
    "tonight", "yesterday", "breaking", "headlines", "live", "announced",
    "transfer", "transfers", "rumour", "rumours", "rumor", "rumors",
    "signing", "signings", "signed", "signs", "injury", "injuries",
    "injured", "fixture", "fixtures", "result", "results", "score", "scores",
}
NEWS_PHRASES = ["this week", "this weekend", "last night", "match report",
                "here we go", "right now"]
QUESTION_WORDS = {
    "who", "whom", "whose", "what", "when", "where", "why", "how", "which",
    "is", "are", "was", "were", "does", "do", "did", "can", "could",
    "should", "will", "would", "explain", "define", "describe", "compare",
    "tell", "difference", "meaning",
}


def detect_intent(query):
    """Return 'news' or 'question' for the text typed by the user."""
    q = normalize(query)
    words = q.split()
    if not words:
        return "news"

    # clear news wording -> always search the news
    if set(words) & NEWS_WORDS or any(p in q for p in NEWS_PHRASES):
        return "news"

    # general question -> answer it directly
    if words[0] in QUESTION_WORDS or str(query).strip().endswith("?"):
        return "question"

    # plain topic like "Messi" or "Premier League" -> news
    return "news"
