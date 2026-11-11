# ⚽ Football News Summary Agent

An AI-powered Football News Summary Agent that retrieves, filters, analyzes, and summarizes the latest football news using Large Language Models (LLMs). Built with Python, LangGraph, Groq, FreeNewsAPI.ai, and Gradio, the application provides an intelligent way to discover football updates and get answers to general football-related questions.


## 📌 Project Overview

The **Football News Summary Agent** is an AI-powered application designed to simplify football news discovery and understanding.

Football fans often need to browse multiple websites to find relevant updates about their favourite clubs, players, competitions, and transfer activities. This project addresses that problem through an intelligent agent that automates the news retrieval and summarization process.

Users can enter a football-related query, and the agent understands the request, searches for relevant articles, evaluates their relevance, removes duplicate content, retrieves additional article information, and generates concise summaries using Groq-powered LLMs.

The application also includes a separate General Football Question Answering module, allowing users to ask questions about football players, clubs, competitions, and rules without unnecessarily triggering a news search.

---

## ✨ Key Features

- **Intelligent Query Understanding:** Identifies football clubs, players, competitions, and topics from user queries.

- **Football News Retrieval:** Retrieves relevant football news using FreeNewsAPI.ai.

- **Relevance Filtering:** Evaluates retrieved articles against the original search query to reduce unrelated results.

- **Duplicate Detection:** Identifies and removes duplicate or highly similar articles.

- **Agentic Workflow:** Uses LangGraph to manage the execution and coordination of different processing stages.

- **Self-Correction Mechanism:** Automatically retries searches with broader queries when insufficient relevant articles are retrieved.

- **Full Article Extraction:** Attempts to retrieve complete article content using FreeNewsAPI, publisher websites, and Jina Reader.

- **AI-Powered Summarization:** Uses Groq-powered LLMs to generate concise and informative football news summaries.

- **LLM Fallback Mechanism:** Supports alternative models when the primary model encounters an error.

- **General Football Q&A:** Answers general football questions through a dedicated question-answering module without executing the news-search workflow.

- **IST Timestamp Conversion:** Converts article publication timestamps into Indian Standard Time (IST).

- **Concurrent Processing:** Uses ThreadPoolExecutor to process multiple articles efficiently.

- **Interactive Gradio Interface:** Provides a football-themed interface with live agent execution traces and summarized reports.

---

## 🧠 Agent Architecture

The project follows a modular architecture in which different Python modules handle specific responsibilities.

| Module | Responsibility |
|---|---|
| `app.py` | Gradio user interface, intent routing, and application execution |
| `agent.py` | LangGraph workflow, orchestration, and self-correction |
| `config.py` | Groq API configuration, model selection, and LLM client initialization |
| `football_qa.py` | General football question answering and intent detection |
| `news_tools.py` | News retrieval, article extraction, URL processing, and duplicate detection |
| `query_parser.py` | Query understanding, normalization, and article relevance evaluation |
| `summarizer.py` | AI-powered article summarization, model fallback, and IST timestamp conversion |

---

## 🔄 How the Agent Works

The application follows two separate execution routes depending on the user's input.

### Route 1: Football News Search and Summarization

1. **User Query:** The user enters a football-related topic, such as Barcelona news or Real Madrid transfer rumours.

2. **Intent Detection:** The system identifies whether the input requires a news search.

3. **Query Planning:** The query parser identifies relevant entities, clubs, players, competitions, and keywords.

4. **News Retrieval:** The LangGraph agent searches for football news using FreeNewsAPI.ai.

5. **Relevance Filtering:** Retrieved articles are evaluated against the original query.

6. **Duplicate Detection:** Duplicate and highly similar articles are identified and removed.

7. **Self-Correction:** If fewer than the required relevant articles are found, the agent broadens the search and retries.

8. **Article Extraction:** The system attempts to retrieve additional article content using multiple extraction methods.

9. **AI Summarization:** Groq-powered LLMs generate concise summaries using the available article content.

10. **Final Report:** The application displays article summaries, publishers, publication timestamps, and original source links.

### Route 2: General Football Question Answering

When a user asks a general football question, the application routes the request directly to the Football Q&A module.

Workflow:

`User Question → Intent Detection → Football Q&A → Groq LLM → Final Answer`

This route avoids unnecessary news retrieval and provides direct answers to questions about football players, clubs, competitions, and rules.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| LangGraph | Agent workflow orchestration |
| LangChain | LLM integration and tool management |
| Groq API | Large Language Model inference |
| FreeNewsAPI.ai | Football news retrieval |
| Gradio | Interactive web application interface |
| Requests | HTTP requests and API communication |
| Trafilatura | Article content extraction |
| Jina Reader | Alternative article extraction |
| ThreadPoolExecutor | Concurrent article processing |

---

## 📂 Project Structure

```text
Football-News-Summary-Agent/
│
├── app.py                  # Gradio application and routing
├── agent.py                # LangGraph agent workflow
├── config.py               # Groq API and model configuration
├── football_qa.py          # General football question answering
├── news_tools.py           # News retrieval and article extraction
├── query_parser.py         # Query understanding and filtering
├── summarizer.py           # AI summarization and IST conversion
│
├── requirements.txt        # Project dependencies
├── .env.example            # Example environment configuration
├── .gitignore              # Git ignored files
└── README.md               # Project documentation
```

---

## ⚙️ Installation and Setup

Follow these steps to run the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/NaveenSingh1011/Football-News-Summary-Agent.git
```

### 2. Navigate to the Project Directory

```bash
cd Football-News-Summary-Agent
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
python -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

### 6. Configure API Keys

The application requires API credentials for Groq and FreeNewsAPI.

**Groq API Key**

1. Visit the Groq developer platform.
2. Sign in to your account.
3. Generate an API key.

[Groq Console – API Keys](https://console.groq.com/keys)

Configure the key in PowerShell:

```powershell
$env:GROQ_API_KEY="YOUR_GROQ_API_KEY"
```

**NewsAPI Key**

Configure your FreeNewsAPI key:

```powershell
$env:FNA_API_KEY="YOUR_FREENEWSAPI_KEY"
```

Replace the placeholders with your actual API keys.

**Important:** These environment variables are required in the current project configuration. Keep your API keys private and never upload them to GitHub.

### 7. Run the Application

```bash
python app.py
```

Once the application starts, Gradio will display a local URL in the terminal.

Open that URL in your browser to interact with the Football News Summary Agent.

---

## 💡 Example Queries

### Football News Search

- Barcelona latest news
- Real Madrid transfer rumours
- Harry Kane news
- Premier League latest updates
- Manchester United injury updates
- Liverpool transfer news

### General Football Questions

- Who is Lionel Messi?
- What is the offside rule in football?
- Explain the UEFA Champions League format.
- What is the difference between a penalty and a free kick?
- Explain the role of a defensive midfielder.
- What is the Ballon d'Or?


## 🚀 Future Enhancements

The project can be extended with the following features:

- Live football match fixtures and results integration.
- Real-time player statistics and performance analysis.
- Dedicated transfer tracking and verification.
- Football club and player comparison tools.
- Historical match analysis and data visualization.
- Persistent conversation history.
- Cloud deployment for wider accessibility.


## ⚠️ Limitations

- News availability depends on the external news API.
- Full article extraction may not work for every publisher.
- Summary quality depends on the availability and reliability of article content.
- Groq API availability, model limits, and rate limits may affect response generation.
- General football answers should not be treated as verified live statistics or breaking news.
- Dedicated live fixture and match-results integration is not part of the current implementation.


## ⭐ Acknowledgements

- [Groq](https://groq.com/) – LLM inference.
- [LangGraph](https://www.langchain.com/langgraph) – Agent workflow orchestration.
- [NewsAPI.ai](https://freenewsapi.ai/) – Football news retrieval.
- [Gradio](https://www.gradio.app/) – Interactive application interface.
