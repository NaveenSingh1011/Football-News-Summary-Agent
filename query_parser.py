import re
import unicodedata


# ==========================================================
# 2. QUERY UNDERSTANDING + RELEVANCE SCORING
# ==========================================================



def normalize(text):
    """Lowercase, strip accents (barça -> barca) and punctuation."""
    text = unicodedata.normalize("NFKD", str(text or ""))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


# canonical name -> words that mean the same thing in an article
ENTITY_ALIASES = {
    # clubs
    "barcelona": ["barcelona", "fc barcelona", "barca"],
    "real madrid": ["real madrid", "madrid"],
    "atletico madrid": ["atletico madrid", "atletico"],
    "manchester united": ["manchester united", "man united", "man utd"],
    "manchester city": ["manchester city", "man city"],
    "liverpool": ["liverpool"],
    "arsenal": ["arsenal"],
    "chelsea": ["chelsea"],
    "tottenham": ["tottenham", "tottenham hotspur", "spurs"],
    "newcastle": ["newcastle", "newcastle united"],
    "aston villa": ["aston villa"],
    "bayern munich": ["bayern munich", "bayern"],
    "borussia dortmund": ["borussia dortmund", "dortmund"],
    "psg": ["psg", "paris saint germain", "paris sg"],
    "juventus": ["juventus", "juve"],
    "inter milan": ["inter milan", "internazionale"],
    "ac milan": ["ac milan", "rossoneri"],
    "napoli": ["napoli"],
    "west ham": ["west ham", "west ham united"],
    "everton": ["everton"],
    "brighton": ["brighton"],
    "brentford": ["brentford"],
    "fulham": ["fulham"],
    "wolves": ["wolves", "wolverhampton"],
    "leicester": ["leicester", "leicester city"],
    "leeds": ["leeds", "leeds united"],
    "nottingham forest": ["nottingham forest"],
    "crystal palace": ["crystal palace"],
    "bournemouth": ["bournemouth"],
    "roma": ["as roma", "roma"],
    "lazio": ["lazio"],
    "atalanta": ["atalanta"],
    "fiorentina": ["fiorentina"],
    "sevilla": ["sevilla"],
    "valencia": ["valencia"],
    "villarreal": ["villarreal"],
    "real sociedad": ["real sociedad"],
    "athletic bilbao": ["athletic bilbao", "athletic club"],
    "benfica": ["benfica"],
    "porto": ["fc porto", "porto"],
    "sporting cp": ["sporting cp", "sporting lisbon"],
    "ajax": ["ajax"],
    "bayer leverkusen": ["bayer leverkusen", "leverkusen"],
    "rb leipzig": ["rb leipzig", "leipzig"],
    "monaco": ["as monaco", "monaco"],
    "marseille": ["marseille", "olympique marseille"],
    "lyon": ["lyon", "olympique lyonnais"],
    # competitions
    "premier league": ["premier league", "epl"],
    "la liga": ["la liga", "laliga"],
    "champions league": ["champions league"],
    "europa league": ["europa league"],
    "serie a": ["serie a"],
    "bundesliga": ["bundesliga"],
    "ligue 1": ["ligue 1"],
    "world cup": ["world cup"],
    # players
    "messi": ["messi", "lionel messi"],
    "ronaldo": ["ronaldo", "cristiano ronaldo"],
    "haaland": ["haaland", "erling haaland"],
    "mbappe": ["mbappe", "kylian mbappe"],
    "yamal": ["yamal", "lamine yamal"],
    "bellingham": ["bellingham", "jude bellingham"],
    "vinicius": ["vinicius", "vinicius junior"],
    "salah": ["salah", "mohamed salah"],
    "kane": ["harry kane"],
    "saka": ["saka", "bukayo saka"],
    "neymar": ["neymar"],
    "lewandowski": ["lewandowski", "robert lewandowski"],
}

# keys of ENTITY_ALIASES that are clubs (not players or competitions)
CLUB_KEYS = {
    "barcelona", "real madrid", "atletico madrid", "manchester united",
    "manchester city", "liverpool", "arsenal", "chelsea", "tottenham",
    "newcastle", "aston villa", "bayern munich", "borussia dortmund", "psg",
    "juventus", "inter milan", "ac milan", "napoli", "west ham", "everton",
    "brighton", "brentford", "fulham", "wolves", "leicester", "leeds",
    "nottingham forest", "crystal palace", "bournemouth", "roma", "lazio",
    "atalanta", "fiorentina", "sevilla", "valencia", "villarreal",
    "real sociedad", "athletic bilbao", "benfica", "porto", "sporting cp",
    "ajax", "bayer leverkusen", "rb leipzig", "monaco", "marseille", "lyon",
}

# topic -> (words in the user's query that trigger it, words that show up in
# an article about that topic)
TOPICS = {
    "transfer": {
        "triggers": {
            "transfer", "transfers", "signing", "signings", "rumour",
            "rumours", "rumor", "rumors", "deal", "deals", "bid", "bids",
            "window"
        },
        "terms": [
            "transfer", "transfers", "signing", "signings", "sign", "signs",
            "signed", "loan", "bid", "deal", "fee", "contract", "medical",
            "join", "joins", "joined", "target", "targets", "linked", "move",
            "offer", "release clause", "agree", "agreed", "swap",
            "here we go", "interest", "interested"
        ],
    },
    "injury": {
        "triggers": {"injury", "injuries", "injured", "fitness"},
        "terms": [
            "injury", "injuries", "injured", "fitness", "ruled out",
            "sidelined", "scan", "surgery", "return", "recovery", "doubt"
        ],
    },
    "match": {
        "triggers": {
            "match", "result", "results", "score", "scores", "fixture",
            "fixtures", "preview"
        },
        "terms": [
            "match", "result", "score", "scored", "win", "won", "draw",
            "defeat", "beat", "fixture", "preview", "goal", "goals"
        ],
    },
    "manager": {
        "triggers": {"manager", "coach", "sacked", "appointed"},
        "terms": [
            "manager", "coach", "head coach", "sacked", "appointed",
            "dismissed", "resign", "resigned", "replace"
        ],
    },
}

STOP_WORDS = {
    "who", "what", "when", "where", "why", "how", "is", "are", "was", "were",
    "the", "a", "an", "of", "for", "to", "in", "on", "and", "or", "me",
    "about", "tell", "show", "give", "please", "latest", "recent", "news",
    "football", "soccer", "updates", "update", "new", "newest", "current",
    "today", "any", "all", "has", "have", "get", "gets", "with", "from",
    "by", "at", "this", "that", "does", "do", "did", "will", "can", "info",
    "information", "story", "stories", "headlines", "now"
}

LATEST_WORDS = {"latest", "recent", "newest", "today", "now", "current"}


def _has(term, text):
    return re.search(r"\b" + re.escape(term) + r"\b", text) is not None


def _count(terms, text):
    return sum(len(re.findall(r"\b" + re.escape(t) + r"\b", text)) for t in terms)


def parse_query(query):
    """Turn a free-text question into entities, topics and API queries."""

    original = str(query or "").strip()
    nq = " " + normalize(original) + " "

    # 1) find known clubs / players / competitions (longest alias first)
    alias_list = sorted(
        ((alias, canon)
         for canon, aliases in ENTITY_ALIASES.items()
         for alias in aliases),
        key=lambda pair: len(pair[0]),
        reverse=True,
    )

    entities = []
    for alias, canon in alias_list:
        if _has(alias, nq):
            if canon not in entities:
                entities.append(canon)
            nq = re.sub(r"\b" + re.escape(alias) + r"\b", " ", nq)

    # 2) find the topic (transfer / injury / ...)
    words = nq.split()
    topics = [
        name for name, cfg in TOPICS.items()
        if any(w in cfg["triggers"] for w in words)
    ]
    topic_words = {w for cfg in TOPICS.values() for w in cfg["triggers"]}

    # 3) any other meaningful word (e.g. an unknown player name) is required
    extra = [
        w for w in words
        if w not in STOP_WORDS and w not in topic_words and len(w) > 1
    ]

    # 4) build cleaner queries for the news API
    api_queries = []
    if entities or topics:
        who = " ".join(e.title() for e in entities)
        extra_text = " ".join(extra)
        base = " ".join(p for p in [who, extra_text] if p)
        variants = []
        for topic in (topics or [""]):
            variants += [f"{base} {topic} news", f"{base} {topic}"]
            if topic == "transfer":
                variants += [
                    f"{base} signing", f"{base} bid",
                    f"{base} deal", f"{base} rumours",
                ]
        variants.append(base)          # plain "Real Madrid" = latest club news
        for variant in variants:
            variant = re.sub(r"\s+", " ", variant).strip()
            if variant and variant.lower() not in [q.lower() for q in api_queries]:
                api_queries.append(variant)
    if original and original.lower() not in [q.lower() for q in api_queries]:
        api_queries.append(original)
    if not api_queries:
        api_queries = ["football"]

    return {
        "original": original,
        "entities": entities,
        "topics": topics,
        "extra": extra,
        "wants_latest": any(w in LATEST_WORDS for w in normalize(original).split()),
        "api_queries": api_queries[:8],
    }


def _club_counts(text, own_aliases, other_clubs):
    """
    Count mentions of the club we want vs. the most-mentioned OTHER club.
    Longest names are matched first, so "Atletico Madrid" is never counted
    as "Madrid".
    """
    pairs = [(a, "xown") for a in own_aliases]
    for club, aliases in other_clubs.items():
        label = "xc" + re.sub(r"[^a-z0-9]", "", club)
        pairs += [(a, label) for a in aliases]
    pairs.sort(key=lambda p: len(p[0]), reverse=True)

    for alias, label in pairs:
        text = re.sub(r"\b" + re.escape(alias) + r"\b", " " + label + " ", text)

    own = len(re.findall(r"\bxown\b", text))
    others = {}
    for tag in re.findall(r"\bxc[a-z0-9]+\b", text):
        others[tag] = others.get(tag, 0) + 1

    return own, (max(others.values()) if others else 0)


def score_article(parsed, article, require_topic=True):
    """
    Return 0 if the article is NOT about what the user asked,
    otherwise a positive relevance score.
    """

    title = normalize(article.get("title"))
    desc = normalize(article.get("description"))
    body = normalize(article.get("content"))
    lead = " ".join(body.split()[:90])           # opening paragraph
    head = f"{title} {desc} {lead}"

    groups = [ENTITY_ALIASES[e] for e in parsed["entities"]]
    groups += [[w] for w in parsed["extra"]]

    # nothing specific requested (e.g. just "football") -> no filtering
    if not groups and not parsed["topics"]:
        return 1.0

    score = 0.0

    # The club / player MUST be a main subject, not a passing mention.
    for terms in groups:

        # Is this group a club the user asked for?
        club_key = next(
            (e for e in parsed["entities"]
             if e in CLUB_KEYS and ENTITY_ALIASES[e] is terms),
            None,
        )

        if club_key:
            # Clubs: the article must be ABOUT this club, not another club
            # that merely mentions it.
            others = {
                c: a for c, a in ENTITY_ALIASES.items()
                if c in CLUB_KEYS and c not in parsed["entities"]
            }
            in_title, other_title = _club_counts(title, terms, others)
            in_desc, other_desc = _club_counts(desc, terms, others)
            in_lead, _ = _club_counts(lead, terms, others)
            in_body, other_body = _club_counts(body, terms, others)

            # must be a main subject (headline / summary / repeated in text)
            if not (in_title > 0 or in_desc > 0
                    or (in_lead > 0 and in_body >= 3) or in_body >= 5):
                return 0.0

            own_weight = 3 * in_title + 2 * in_desc + in_body
            other_weight = 3 * other_title + 2 * other_desc + other_body

            # another club dominates the article -> not about this club
            if other_weight > own_weight:
                return 0.0
            if other_weight == own_weight and in_title == 0:
                return 0.0

        else:
            # players, competitions and other keywords
            in_title = _count(terms, title)
            in_desc = _count(terms, desc)
            in_lead = _count(terms, lead)
            in_body = _count(terms, body)

            if not (in_title > 0 or in_desc > 0 or in_lead > 0 or in_body >= 5):
                return 0.0

        score += (5 if in_title else 0) + (3 if in_desc else 0)
        score += (2 if in_lead else 0) + min(in_body, 5) * 0.4

    # The topic (transfer, injury...) must be present too.
    if parsed["topics"] and require_topic:
        best = 0.0
        for topic in parsed["topics"]:
            terms = TOPICS[topic]["terms"]
            in_title = _count(terms, title)
            in_head = _count(terms, head)
            in_body = _count(terms, body)

            if in_head > 0 or in_body >= 2:
                best = max(
                    best,
                    (2 if in_title else 0) + (1 if in_head else 0)
                    + min(in_body, 5) * 0.2
                )
        if best == 0.0:
            return 0.0
        score += best

    return max(score, 0.1)
