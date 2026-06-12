# NyayaSetu — RAG-Powered Legal Assistant

NyayaSetu ("bridge to justice") is a RAG-powered legal assistant that helps everyday Indians understand their rights under common laws. Instead of reading dense government PDFs, users ask plain questions like *"can my employer deduct salary without notice"* and get clear, cited answers grounded in official legal documents.

Built with **LangGraph** for a self-corrective retrieval workflow, **ChromaDB** for vector storage, **Google Gemini** for LLM and embeddings, and served via **FastAPI**.

---

## Architecture

```
User Question
      │
      ▼
┌─────────────┐
│   Query     │  Rewrites query for better retrieval,
│  Analysis   │  classifies legal category
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Retrieval  │  Searches ChromaDB for top-5 relevant chunks
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Document   │  LLM grades each chunk as relevant/irrelevant
│  Grading    │
└──────┬──────┘
       │
       ├── sufficient docs? ──► YES ──► Generation ──► Hallucination Check ──► Answer
       │
       └── NO ──► retry_count < 2? ──► YES ──► Rewrite & Re-retrieve (loop)
                                  └──► NO  ──► Web Search Fallback ──► Generation ──► Answer
```

The workflow is implemented as a **LangGraph StateGraph** with conditional edges for self-correction. If retrieved documents are graded as irrelevant, the system rewrites the query and retries (up to 2 times). After retries are exhausted, it falls back to web search via Tavily before generating the final answer.

### Bonus Features
- **Hallucination Check**: After generation, a verification node checks if the answer is grounded in the retrieved context. Hallucinated answers are regenerated with a stricter prompt.
- **Web Search Fallback**: When the local corpus has no relevant results, Tavily web search provides additional context.
- **Conversation Memory**: Session-based chat history supports follow-up questions.

---

## Corpus

The system ingests 9 official Indian legal documents covering:
- Consumer Protection Act, 2019
- Labour Codes (compilation of 4 codes)
- Payment of Gratuity Act, 1972
- Motor Vehicles Act, 1988
- Right to Information Act, 2005
- Rajasthan Rent Control Act, 2001

Documents are stored as PDFs in `data/docs/` and indexed into ChromaDB at `data/chroma/`.

---

## Setup

### Prerequisites
- Python 3.10+
- A Google Gemini API key ([get one here](https://aistudio.google.com/app/apikey))
- A Tavily API key for web search fallback ([sign up here](https://tavily.com))

### Installation

```bash
git clone https://github.com/A-Square8/NyayaSetu.git
cd NyayaSetu

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### Ingest Documents

Place your legal PDFs in `data/docs/` (or run the fetch script), then build the vector index:

```bash
python scripts/fetch_corpus.py
python src/ingest.py
```

### Run the Server

```bash
uvicorn app:api --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

## API Endpoints

### POST /query
Submit a legal question and get a cited answer.

**Request:**
```json
{
  "question": "Can my employer deduct salary without notice?",
  "session_id": "optional-session-id-for-follow-ups"
}
```

**Response:**
```json
{
  "answer": "Under the Payment of Wages Act and the Labour Codes, an employer cannot make unauthorized deductions from wages without prior notice...",
  "sources": ["data/docs/Labour Act.pdf", "data/docs/PaymentofGratuityAct.pdf"],
  "category": "labour rights"
}
```

### POST /ingest
Upload new PDF documents to the corpus.

```bash
curl -X POST http://localhost:8000/ingest \
  -F "files=@new_document.pdf"
```

### GET /documents
List all documents currently in the corpus.

**Response:**
```json
[
  {"filename": "CPA2019.pdf", "size_bytes": 1236998},
  {"filename": "Labour Act.pdf", "size_bytes": 1476614}
]
```

### POST /feedback
Submit feedback on an answer.

**Request:**
```json
{
  "question": "Can my employer deduct salary without notice?",
  "answer": "Under the Payment of Wages Act...",
  "rating": "up",
  "comment": "Very helpful and accurate"
}
```

---

## Design Decisions & Tradeoffs

### Chunking Strategy
- **Chunk size: 1000 characters with 200 overlap**. Legal documents have long sections, so a 1000-char window captures enough context per chunk while keeping retrieval precise. The 200-char overlap prevents important sentences from being split across chunks.

### Embedding Model
- **Sentence-Transformers (all-MiniLM-L6-v2)**. Chosen to bypass Google's free-tier rate limits (100 RPM). It runs entirely locally, is free, and is perfectly lightweight for this size of corpus while providing excellent retrieval accuracy.

### LLM Choice
- **Gemini 1.5 Flash**. Free tier, fast inference, strong structured output support. Used across all nodes (query analysis, grading, generation, hallucination check).

### Self-Corrective Retrieval
- The grading + retry loop (max 2 retries) is the core self-corrective mechanism. If the initial retrieval misses, the query gets rewritten and re-tried. This handles ambiguous or colloquial queries that don't match legal terminology on the first attempt.

### Hallucination Check
- A separate verification node (inspired by Self-RAG) checks that the generated answer is actually grounded in the retrieved documents. This is critical for legal Q&A where accuracy matters.

### Web Search Fallback
- Tavily web search kicks in only after local retries are exhausted. This ensures the system can still answer questions outside the corpus without polluting answers that the local docs can handle.

---

## What I Would Improve With More Time
- Add a Streamlit/Gradio frontend for interactive Q&A
- Implement hybrid search (keyword + semantic) for better retrieval on legal terminology
- Add document-level metadata (act name, section numbers) for more precise citations
- Support Hindi language queries with multilingual embeddings
- Add evaluation metrics (retrieval precision, answer faithfulness scores)
- Deploy with Docker for easier setup

---

## Project Structure

```
├── app.py                    # FastAPI application
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── scripts/
│   └── fetch_corpus.py       # Downloads legal PDFs
├── src/
│   ├── graph.py              # LangGraph workflow definition
│   ├── ingest.py             # Document ingestion pipeline
│   ├── state.py              # Graph state schema
│   └── nodes/
│       ├── query_analysis.py # Query rewriting + classification
│       ├── retrieval.py      # Vector store search
│       ├── grading.py        # Document relevance grading
│       ├── generation.py     # Answer generation with citations
│       ├── hallucination.py  # Answer groundedness check
│       └── web_search.py     # Tavily web search fallback
├── data/
│   ├── docs/                 # PDF corpus (not tracked in git)
│   └── chroma/               # ChromaDB index (not tracked in git)
└── test.py                   # End-to-end test script
```
