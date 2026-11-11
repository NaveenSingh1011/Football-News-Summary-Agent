import re
import os
from difflib import SequenceMatcher
from urllib.parse import urlsplit

import requests
import trafilatura
from langchain_core.tools import tool

from config import BASE_URL
from query_parser import normalize


# ==========================================================
# API CONFIGURATION
# ==========================================================

def get_api_headers():
    """Return authentication headers for FreeNewsAPI."""

    api_key = os.getenv("FNA_API_KEY")

    if not api_key:
        raise ValueError(
            "FreeNewsAPI key is missing. "
            "Set the FNA_API_KEY environment variable."
        )

    return {
        "Authorization": f"Bearer {api_key}"
    }


# ==========================================================
# 3. NEWS FETCHING HELPERS
# ==========================================================

def extract_article_text(data):
    """Extract article body text from an API response."""

    if not isinstance(data, dict):
        return ""

    nested = data.get("article")

    if isinstance(nested, dict):
        data = nested

    for field in [
        "full_text",
        "body",
        "text",
        "content",
        "article_text",
        "body_text"
    ]:
        value = data.get(field)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


def _search_api(query, size=10):
    """Search football news using authenticated FreeNewsAPI."""

    headers = get_api_headers()

    response = requests.get(
        f"{BASE_URL}/v1/search",
        headers=headers,
        params={
            "q": query,
            "lang": "en",
            "size": min(max(int(size), 1), 10),
            "full_text": "true",
            "sort": "date",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return data.get("results", [])


# ==========================================================
# BROWSER HEADERS
# ==========================================================

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ==========================================================
# ARTICLE QUALITY CHECKS
# ==========================================================

BAD_TEXT_HINTS = [
    "enable javascript",
    "enable cookies",
    "accept all cookies",
    "subscribe to continue",
    "subscribe to read",
    "are you a robot",
    "access denied",
    "verify you are human",
    "sign in to continue",
    "checking your browser",
]


def _good_text(text, min_words=80):
    """Check whether extracted text looks like a real article."""

    if not text:
        return False

    if len(text.split()) < min_words:
        return False

    return not any(
        hint in text[:600].lower()
        for hint in BAD_TEXT_HINTS
    )


# ==========================================================
# ARTICLE FETCHING METHODS
# ==========================================================

def _from_news_api(link):
    """Method 1: Fetch article using FreeNewsAPI."""

    headers = get_api_headers()

    response = requests.get(
        f"{BASE_URL}/v1/article",
        headers=headers,
        params={
            "url": link
        },
        timeout=20,
    )

    response.raise_for_status()

    return extract_article_text(response.json())


def _from_publisher(link):
    """Method 2: Download article directly from publisher."""

    response = requests.get(
        link,
        headers=BROWSER_HEADERS,
        timeout=15,
    )

    response.raise_for_status()

    return trafilatura.extract(
        response.text,
        include_comments=False,
        include_tables=False,
    ) or ""


def _from_reader(link):
    """Method 3: Extract article using Jina Reader."""

    response = requests.get(
        "https://r.jina.ai/" + link,
        headers={
            "Accept": "text/plain"
        },
        timeout=30,
    )

    response.raise_for_status()

    text = response.text

    if "Markdown Content:" in text:
        text = text.split("Markdown Content:", 1)[1]

    # Remove Markdown images
    text = re.sub(
        r'!\[[^\]]*\]\([^)]+\)',
        " ",
        text
    )

    # Convert Markdown links into plain text
    text = re.sub(
        r'\[([^\]]+)\]\([^)]+\)',
        r'\1',
        text
    )

    return text


# ==========================================================
# GET FULL ARTICLE TEXT
# ==========================================================

def get_full_text(link, current=""):
    """
    Try multiple methods to retrieve the full article.
    Return the first valid article or the longest available text.
    """

    best = current or ""

    methods = [
        ("news API", _from_news_api),
        ("publisher page", _from_publisher),
        ("reader service", _from_reader),
    ]

    for name, method in methods:

        try:
            text = re.sub(
                r"\s+",
                " ",
                method(link) or ""
            ).strip()

        except Exception as error:
            print(
                f"  [{name}] failed for {link[:55]}: "
                f"{str(error)[:120]}"
            )
            continue

        if _good_text(text):
            print(
                f"  Full text via {name}: "
                f"{len(text.split())} words"
            )
            return text

        if len(text) > len(best):
            best = text

    print(f"  Could not get full text for {link[:55]}")

    return best


# ==========================================================
# URL AND DUPLICATE CHECKS
# ==========================================================

def canonical_url(url):
    """Remove tracking differences from URLs."""

    parts = urlsplit(str(url or ""))

    host = parts.netloc.lower().replace("www.", "")

    return host + parts.path.rstrip("/").lower()


def is_duplicate(article, kept):
    """
    Identify duplicate articles using:
    1. Exact headline matching
    2. Similar headline matching
    3. Identical opening text
    """

    title = normalize(article.get("title"))

    lead = normalize(
        article.get("content")
    )[:200]

    for other in kept:

        other_title = normalize(
            other.get("title")
        )

        if title == other_title:
            return True

        if SequenceMatcher(
            None,
            title,
            other_title
        ).ratio() >= 0.85:
            return True

        other_lead = normalize(
            other.get("content")
        )[:200]

        if len(lead) >= 150 and lead == other_lead:
            return True

    return False


# ==========================================================
# 5. AGENT TOOLS
# ==========================================================

@tool
def search_news(query: str, limit: int = 10) -> list:
    """Search football news and return relevant articles."""

    articles = []

    try:

        results = _search_api(
            query,
            size=limit
        )

        for item in results:

            title = item.get("title") or ""
            link = item.get("url") or ""

            if title and link:

                articles.append({
                    "title": title,

                    "source": (
                        item.get("sitename")
                        or item.get("host")
                        or "Unknown"
                    ),

                    "published_at": (
                        item.get("published_at") or ""
                    ),

                    "description": (
                        item.get("description") or ""
                    ),

                    "content": extract_article_text(item),

                    "url": link,
                })

        print(
            f"[NEWS] Retrieved {len(articles)} "
            f"articles for: {query}"
        )

        return articles

    except Exception as error:

        print(
            f"[NEWS ERROR] Search failed for "
            f"'{query}': {error}"
        )

@tool
def fetch_full_article(url: str) -> str:
    """Retrieve the complete text of a football news article."""

    return get_full_text(url)