import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional

# LangChain & Google Gemini
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Load env vars
load_dotenv()

API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not set in .env")
if not API_BEARER_TOKEN:
    raise ValueError("API_BEARER_TOKEN not set in .env")

PDF_PATH = "policy.pdf"

app = FastAPI(title="HackRx Policy QA API", docs_url="/api/v1/docs")

qa_chain: Optional[RetrievalQA] = None
vector_store: Optional[FAISS] = None
security = HTTPBearer()

class QueryRequest(BaseModel):
    documents: Optional[str] = None
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True

@app.on_event("startup")
async def startup_event():
    global qa_chain, vector_store

    if not os.path.exists(PDF_PATH):
        print(f"ERROR: {PDF_PATH} not found.")
        return

    try:
        loader = PyPDFLoader(PDF_PATH)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        docs = text_splitter.split_documents(documents)

        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
        vector_store = FAISS.from_documents(docs, embeddings)

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY
        )

        prompt_template = """
        You are a strict insurance policy expert.
        For each question, extract exact clauses, limits, waiting periods, or exclusions from the context.
        Do not guess or explain anything not present.
        Respond in a single paragraph. If not found, say: "Information not found in the provided documents."

        Context:
        {context}

        Question:
        {question}

        Answer:
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
            chain_type_kwargs={"prompt": prompt}
        )

        print("✅ LLM system initialized successfully.")

    except Exception as e:
        print(f"❌ ERROR during startup: {e}")

async def _call_qa_chain_with_retry(qa_chain_instance, query_dict, retries=4, delay=4):
    for i in range(retries):
        try:
            return await qa_chain_instance.ainvoke(query_dict)
        except Exception as e:
            if "quota" in str(e).lower():
                print(f"Quota error, retrying in {delay * (2 ** i)}s...")
                await asyncio.sleep(delay * (2 ** i))
            else:
                raise e
    raise Exception("Max retries reached")

@app.post("/hackrx/run", response_model=QueryResponse, dependencies=[Depends(verify_token)])
async def run_submission(request: QueryRequest):
    if qa_chain is None:
        raise HTTPException(503, "LLM not ready")

    try:
        tasks = [_call_qa_chain_with_retry(qa_chain, {"query": q}) for q in request.questions]
        results = await asyncio.gather(*tasks)
        answers = [r.get("result", "Information not found in the provided documents.") for r in results]
        return {"answers": answers}
    except Exception as e:
        raise HTTPException(500, f"Processing failed: {str(e)}")

@app.get("/", include_in_schema=False)
def root():
    return {"message": "HackRx Insurance QA API is running. Visit /api/v1/docs."}
