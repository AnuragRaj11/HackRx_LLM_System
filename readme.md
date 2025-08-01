HackRx 6.0: LLM-Powered Intelligent Query–Retrieval System
Project Overview
This project delivers an LLM-Powered Intelligent Query–Retrieval System designed to extract precise, contextual answers from large unstructured documents (e.g., insurance policies, legal contracts). Built with FastAPI and leveraging Google Gemini models via LangChain, it aims to enhance information retrieval efficiency in critical domains like insurance, legal, HR, and compliance.

Features
Document Processing: Ingests local PDF documents, extracts text, and chunks content.

Semantic Search: Uses Google Generative AI Embeddings and FAISS (local vector store) for efficient semantic retrieval.

LLM-Powered Reasoning: Employs Google Gemini 1.5 Flash via LangChain for accurate answer generation and contextual decision-making.

API Interface: Provides a secure FastAPI endpoint for seamless integration.

Performance: Optimized for quick responses by pre-loading and indexing documents at startup.

Architecture
The system implements a Retrieval Augmented Generation (RAG) pattern:

Ingestion: Local PDF documents are loaded, chunked, and embedded.

Indexing: Embeddings are stored in a local FAISS vector database.

Query: User queries are embedded and used to retrieve relevant document chunks from FAISS.

Generation: Google Gemini processes the query and retrieved context to generate a precise answer.

graph TD
    A[Local PDF Documents] --> B[Load & Chunk]
    B --> C[Embeddings]
    C --> D[FAISS Vector Store]
    
    E[User Query] --> F[Query Embedding]
    F --> D
    
    D -- Relevant Chunks --> G[Google Gemini LLM]
    G --> H[Answer]

Setup & Run Instructions
Follow these steps to get the system running:

1. Project Setup
Clone the repository (if applicable) and navigate into the project directory (HackRx_LLM_System).

Create source_pdfs/ folder and place your individual policy PDFs (e.g., BAJHLIP23020V012223.pdf, etc.) inside it.

Create a .env file in the project root and add your Google API Key:

GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"

(Ensure this key has access to Google Gemini models.)

2. Install Dependencies
Create and activate a Python virtual environment:

python -m venv venv
# Windows: .\venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

Install required packages (using the requirements.txt provided in the project files):

pip install -r requirements.txt

3. Prepare Documents
Merge your individual PDFs into a single policy.pdf using the merge_pdfs.py script:

python merge_pdfs.py

(This will create policy.pdf in your project root.)

4. Run the API
With your virtual environment activated, start the FastAPI server:

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

(The server will initialize the RAG system on startup, which may take a few minutes.)

How to Test
Open your browser to the API documentation: http://localhost:8000/api/v1/docs

Click POST /hackrx/run, then "Try it out".

In the Request body, use the sample JSON (the documents URL is ignored; policy.pdf is used locally):

{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=...",
    "questions": [
        "Does this policy cover knee surgery, and what are the conditions?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?"
    ]
}

Set the Authorization header to Bearer 74b1158d301e42af454a706d7610b664511de7b16c859c882a6bbb02cc936ed8.

Click "Execute" to see the answers.

API Endpoint
POST /hackrx/run: Processes a list of natural language questions.

Authentication: Bearer Token (74b1158d301e42af454a706d7610b664511de7b16c859c882a6bbb02cc936ed8)

Request Body: {"documents": "string (ignored)", "questions": ["string"]}

Response Body: {"answers": ["string"]}

Evaluation Parameters
Accuracy: Precision of query understanding and clause matching.

Token Efficiency: Optimized LLM token usage.

Latency: Response speed.

Reusability: Code modularity.

Explainability: Clear decision reasoning (inherent in RAG process).

Tech Stack
Backend: FastAPI

LLM & Embeddings: Google Gemini (via LangChain)

Vector Database: FAISS (local)

Document Parsing: pypdf

Environment: python-dotenv