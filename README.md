# Football News Summary Agent

## Project structure

- config.py: Groq key, model names, API base URL
- query_parser.py: understands the query and scores article relevance
- news_tools.py: news search and full-article fetching (agent tools)
- football_qa.py: direct answers for general football questions
- summarizer.py: LLM summary calls with retries and model fallback
- agent.py: LangGraph agent (plan, search, filter, retry, enrich, summarize, report)
- app.py: Gradio interface that shows the live agent trace


Requires Python 3.10 or newer.
