# Finance-assistant
# Folder Structure (as a comment reference)
# finance_assistant/
# ├── data_ingestion/
# ├── agents/
# ├── orchestrator/
# ├── streamlit_app/
# ├── docs/
# │   └── ai_tool_usage.md
# ├── README.md
# ├── Dockerfile
# └── requirements.txt

# requirements.txt content (can be pip installed)
requirements = """
fastapi
uvicorn
requests
beautifulsoup4
yfinance
openai
langchain
faiss-cpu
sentence-transformers
python-dotenv
streamlit
whisper
coqui-ai
pyttsx3
pydub
"""

# Save the requirements to file
with open("requirements.txt", "w") as f:
    f.write(requirements)

# Sample placeholder for README.md content
readme = """
# Multi-Agent Finance Assistant

## Architecture Diagram

```mermaid
flowchart TD
    A[Voice Input (Mic)] --> B[STT (Whisper)]
    B --> C[Orchestrator (FastAPI)]
    C --> D1[API Agent (Yahoo Finance)]
    C --> D2[Scraping Agent (Earnings Reports)]
    C --> D3[Retriever Agent (FAISS Index)]
    D1 --> E[Analysis Agent]
    D2 --> E
    D3 --> E
    E --> F[Language Agent (LLM via Langchain)]
    F --> G[TTS (Coqui / pyttsx3)]
    G --> H[Streamlit App Output]
```

## Folder Structure
```
/data_ingestion       → API + scraper logic
/agents               → FastAPI microservices for each agent
/orchestrator         → Routing logic (voice → agents)
/streamlit_app        → UI layer for interaction
/docs                 → AI usage log, diagrams, notes
```

## Setup
```bash
git clone <repo>
cd finance_assistant
pip install -r requirements.txt
```

## Run Services
```bash
uvicorn agents.api_agent:app --reload
uvicorn agents.scraper_agent:app --reload
uvicorn orchestrator.main:app --reload
streamlit run streamlit_app/app.py
```
"""

with open("README.md", "w") as f:
    f.write(readme)

# Create empty AI tool usage log
open("docs/ai_tool_usage.md", "w").close()
