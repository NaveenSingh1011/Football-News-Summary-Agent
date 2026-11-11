
import gradio as gr

from agent import agent
from football_qa import detect_intent, answer_football_question


# ==========================================================
# 1. RUN AGENT - ORIGINAL AGENT FUNCTIONALITY
# ==========================================================

def run_agent(topic, number_of_articles):

    topic = str(topic or "").strip() or "football"
    trace = []

    # Router: general questions are answered directly,
    # without performing a news search.

    if detect_intent(topic) == "question":

        trace.append(
            "[router] ROUTE: general football question, no news search"
        )

        yield (
            "\n".join(trace),
            f"**Question:** {topic}\n\n{answer_football_question(topic)}"
        )

        return

    # Initial LangGraph state

    initial = {
        "query": topic,
        "limit": int(number_of_articles or 5),

        "parsed": {},
        "attempt": 0,
        "candidates": [],
        "relevant": [],

        "relaxed": False,
        "articles": [],
        "summaries": [],
        "report": "",

        "trace": [],
    }

    report = "Working..."

    try:

        for step in agent.stream(initial, stream_mode="updates"):

            for node, update in step.items():

                for line in update.get("trace", []):

                    trace.append(f"[{node}] {line}")

                if update.get("report"):

                    report = update["report"]

            yield "\n".join(trace), report

    except Exception as error:

        trace.append(
            f"[error] {type(error).__name__}: {error}"
        )

        yield (
            "\n".join(trace),
            "## Error\n\nThe agent stopped. See the trace above."
        )


# ==========================================================
# 2. CLEAR CHAT FUNCTION
# ==========================================================

def clear_chat():

    return (
        "",
        "",
        "Enter a topic and click Run Agent."
    )


# ==========================================================
# 3. CUSTOM CSS - FOOTBALL THEME
# ==========================================================

custom_css = """

/* ==========================================
   GLOBAL BACKGROUND
========================================== */

.gradio-container {

    background: linear-gradient(
        135deg,
        #0b1712,
        #14251c,
        #0b1712
    ) !important;

    max-width: 100% !important;
}

.main-container {

    max-width: 1250px !important;

    margin: auto !important;

    padding: 10px 20px !important;
}


/* ==========================================
   HEADER
========================================== */

.header-card {

    text-align: center;

    padding: 20px;

    margin-bottom: 12px;

    border-radius: 16px;

    background: linear-gradient(
        120deg,
        #087443,
        #064e36,
        #102c20
    );

    border: 1px solid #269966;

    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
}

.header-card h1 {

    color: #ffffff !important;

    font-size: 30px !important;

    font-weight: 800 !important;

    margin: 0 0 6px 0 !important;
}

.header-card p {

    color: #e0f5e9 !important;

    font-size: 14px !important;

    margin: 4px 0 !important;
}


/* =========================================
   SEARCH CARD
========================================= */

.input-card {
    background: #ffffff !important;
    padding: 14px 18px !important;
    border-radius: 15px !important;
    border: 1px solid #dce8e0 !important;
    margin-bottom: 10px !important;
}

/* Search labels */

.input-card label {
    color: #1c3025 !important;
    font-size: 13px !important;
    font-weight: 650 !important;
    margin-bottom: 5px !important;
}

/* Search textbox */

.input-card input {
    background: #f8faf9 !important;
    color: #17291f !important;
    border: 1px solid #cbd9d0 !important;
    border-radius: 10px !important;
    height: 46px !important;
    min-height: 46px !important;
    font-size: 15px !important;
}

/* Placeholder */

.input-card input::placeholder {
    color: #78877e !important;
    opacity: 1 !important;
}

/* Article selector */

.article-count {
    min-width: 155px !important;
    max-width: 175px !important;
}

.article-count label {
    white-space: nowrap !important;
}

.article-count input {
    height: 46px !important;
    min-height: 46px !important;
    background: #f0f7f2 !important;
    color: #087443 !important;
    border: 1.5px solid #a8cdb5 !important;
    border-radius: 10px !important;
    font-size: 21px !important;
    font-weight: 750 !important;
    text-align: center !important;
}

/* Buttons spacing */

.input-card .run-btn,
.input-card .clear-btn {
    margin-top: 5px !important;
}

/* ==========================================
   NUMBER OF ARTICLES
========================================== */

#search-panel .article-count {

    min-width: 190px !important;

    max-width: 190px !important;

    flex: 0 0 190px !important;
}


/* Keep label on one line */

#search-panel .article-count label {

    white-space: nowrap !important;

    font-size: 13px !important;
}


/* Dropdown */

#search-panel .article-count input {

    background: #f0f7f2 !important;

    color: #087443 !important;

    border: 1.5px solid #a8cdb5 !important;

    border-radius: 10px !important;

    height: 46px !important;

    min-height: 46px !important;

    font-size: 21px !important;

    font-weight: 750 !important;

    text-align: center !important;
}


/* Dropdown options */

.article-count ul {

    background: #ffffff !important;
}

.article-count li {

    color: #17291f !important;

    text-align: center !important;
}


/* ==========================================
   ACTION BUTTONS
========================================== */

#action-buttons {

    margin-top: 7px !important;

    padding-top: 0 !important;

    gap: 8px !important;
}

#action-buttons .wrap {

    margin-bottom: 0 !important;
}


/* Run Agent */

.run-btn button {

    background: linear-gradient(
        90deg,
        #07834b,
        #16a765
    ) !important;

    color: #ffffff !important;

    border: none !important;

    border-radius: 10px !important;

    font-size: 15px !important;

    font-weight: 700 !important;

    min-height: 44px !important;

    transition: 0.2s ease;
}

.run-btn button:hover {

    background: #087c49 !important;

    transform: translateY(-1px);
}


/* Clear Chat */

.clear-btn button {

    background: #26372d !important;

    color: #ffffff !important;

    border: 1px solid #64796a !important;

    border-radius: 10px !important;

    font-weight: 600 !important;

    min-height: 44px !important;
}

.clear-btn button:hover {

    background: #3b5042 !important;
}


/* ==========================================
   AGENT TRACE SECTION
========================================== */

#agent-trace {

    background: #14231b !important;

    border: 1px solid #4a8b61 !important;

    border-radius: 14px !important;

    padding: 12px !important;

    margin-top: 8px !important;

    color: #ffffff !important;
}


/* Agent Trace heading */

#agent-trace > button,
#agent-trace button,
#agent-trace summary,
#agent-trace [role="button"] {

    background: #203d2c !important;

    color: #E5E7EB !important;

    -webkit-text-fill-color: #E5E7EB !important;

    border: 1px solid #426c50 !important;

    border-radius: 9px !important;

    font-size: 16px !important;

    font-weight: 750 !important;

    padding: 13px !important;
}


/* Force heading text to light grey */

#agent-trace button *,
#agent-trace summary *,
#agent-trace [role="button"] * {

    color: #E5E7EB !important;

    -webkit-text-fill-color: #E5E7EB !important;

    fill: #E5E7EB !important;

    stroke: #E5E7EB !important;
}


/* Agent Trace textbox */

#agent-trace textarea {

    background: #0c1711 !important;

    color: #b8f5ce !important;

    -webkit-text-fill-color: #b8f5ce !important;

    border: 1px solid #42664e !important;

    border-radius: 10px !important;

    font-size: 13px !important;

    line-height: 1.6 !important;
}


/* Trace placeholder */

#agent-trace textarea::placeholder {

    color: #a8cbb5 !important;

    -webkit-text-fill-color: #a8cbb5 !important;

    opacity: 1 !important;
}


/* ==========================================
   FOOTBALL INTELLIGENCE REPORT
========================================== */

.report-card {

    background: #ffffff !important;

    border: 1px solid #e0e8e2 !important;

    border-radius: 16px !important;

    padding: 20px !important;

    margin-top: 14px !important;

    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}


/* Report text */

.report-card,
.report-card p,
.report-card li,
.report-card span,
.report-card strong,
.report-card h1,
.report-card h2,
.report-card h3,
.report-card h4 {

    color: #202c25 !important;
}


/* Report headings */

.report-card h1,
.report-card h2,
.report-card h3 {

    color: #087443 !important;

    font-weight: 750 !important;
}


/* Report paragraphs */

.report-card p,
.report-card li {

    font-size: 15px !important;

    line-height: 1.7 !important;
}


/* Bold text */

.report-card strong {

    color: #075c37 !important;
}


/* Article links */

.report-card a {

    color: #087c49 !important;

    font-weight: 600 !important;

    text-decoration: underline !important;
}


/* Horizontal separators */

.report-card hr {

    border-color: #dce6df !important;
}


/* ==========================================
   FOOTER
========================================== */

.footer-text {

    text-align: center;

    color: #a8c2b1 !important;

    font-size: 12px;

    padding: 12px;

    line-height: 1.8;
}

"""


# ==========================================================
# 4. GRADIO INTERFACE
# ==========================================================

with gr.Blocks(
    title="Football News Summary Agent"
) as demo:

    with gr.Column(elem_classes=["main-container"]):


        # ======================================
        # HEADER
        # ======================================

        gr.HTML("""
        <div class="header-card">

            <h1>⚽ Football News Summary Agent</h1>

            <p>
                An agent that plans its search, calls news tools, checks its own results,
                  retries when needed, and summarizes the articles.
            </p>

        </div>
        """)


        # ======================================
        # SEARCH SECTION
        # ======================================

        with gr.Group(elem_classes=["input-card"]):

            with gr.Row(equal_height=True):

                topic_input = gr.Textbox(
                    label="Search Football News",
                    placeholder="e.g. Barcelona latest transfer news, Messi, Premier League",
                    value="",
                    scale=6,
                    min_width=300,
                    lines=1
                )

                article_count = gr.Dropdown(
                    choices=[3, 5, 10],
                    value=5,
                    label="Number of Articles",
                    scale=1,
                    min_width=155,
                    elem_classes=["article-count"]
                )

            # ACTION BUTTONS

            with gr.Row(equal_height=True, elem_id="action-buttons"):

                run_button = gr.Button(
                    "⚽ Run Agent",
                    variant="primary",
                    elem_classes=["run-btn"],
                    scale=4
                )

                clear_button = gr.Button(
                    "🗑️ Clear Chat",
                    elem_classes=["clear-btn"],
                    scale=1
                )


        # ======================================
        # AGENT TRACE
        # ORIGINAL SIZE RESTORED
        # ======================================

        with gr.Accordion(

            "⚙️ Agent Trace - Planning, Tool Calls & Self-Correction",

            open=True,

            elem_id="agent-trace"

        ):

            trace_box = gr.Textbox(

                lines=16,

                max_lines=30,

                interactive=False,

                show_label=False,

                placeholder="Agent execution steps will appear here..."

            )


        # ======================================
        # FOOTBALL INTELLIGENCE REPORT
        # ======================================

        with gr.Column(elem_classes=["report-card"]):

            gr.Markdown(
                "### 📰Summarized Report"
            )

            report_box = gr.Markdown(
                "Enter a topic and click Run Agent."
            )


        # ======================================
        # FOOTER
        # ======================================

        gr.HTML("""
        <div class="footer-text">

            ⚽ Powered by LangGraph | Groq AI | FreeNewsAPI.ai

            <br>

            Football Intelligence • AI-Powered News Summarization

        </div>
        """)


    # ==========================================
    # RUN AGENT
    # ==========================================

    run_button.click(

        fn=run_agent,

        inputs=[
            topic_input,
            article_count
        ],

        outputs=[
            trace_box,
            report_box
        ]
    )


    # ==========================================
    # SEARCH USING ENTER KEY
    # ==========================================

    topic_input.submit(

        fn=run_agent,

        inputs=[
            topic_input,
            article_count
        ],

        outputs=[
            trace_box,
            report_box
        ]
    )


    # ==========================================
    # CLEAR CHAT
    # ==========================================

    clear_button.click(

        fn=clear_chat,

        inputs=[],

        outputs=[
            topic_input,
            trace_box,
            report_box
        ]
    )


# ==========================================================
# 5. LAUNCH APPLICATION
# ==========================================================

demo.launch(

    share=True,

    debug=True,

    theme=gr.themes.Soft(
        primary_hue="green",
        secondary_hue="emerald",
        neutral_hue="slate"
    ),

    css=custom_css

)

