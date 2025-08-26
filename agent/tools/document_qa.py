# type: ignore
import sys
import types
if sys.platform == "win32":
    sys.modules["pwd"] = types.SimpleNamespace(getpwuid=lambda x: None)
from langchain.tools import tool
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.word_document import Docx2txtLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from agent.config.settings import GROQ_API_KEY, DOCUMENTS_DIR
import os
import shutil

vector_store = None
embeddings = None

def load_documents_from_dir(documents_dir: str):
    """Load supported documents dynamically from a folder."""
    documents = []
    for root, _, files in os.walk(documents_dir):
        for file in files:
            file_path = os.path.join(root, file)
            ext = file.lower()
            try:
                if ext.endswith(".pdf"):
                    docs = PyPDFLoader(file_path).load()
                elif ext.endswith(".docx"):
                    docs = Docx2txtLoader(file_path).load()
                elif ext.endswith(".txt"):
                    docs = TextLoader(file_path).load()
                else:
                    continue
                documents.extend(docs)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    return documents

def initialize_document_qa():
    """Initialize the document QA system."""
    global vector_store, embeddings
    if vector_store is not None:
        return vector_store
    if not os.path.exists(DOCUMENTS_DIR):
        os.makedirs(DOCUMENTS_DIR)
        return None
    documents = load_documents_from_dir(DOCUMENTS_DIR)
    if not documents:
        return None
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(texts, embeddings)
    return vector_store

@tool
def document_qa(question: str) -> str:
    """Answers questions based on documents in the local knowledge base using RAG."""
    try:
        vector_store = initialize_document_qa()
        if vector_store is None:
            return "No documents found in data/documents/. Please add files."
        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatGroq(api_key=GROQ_API_KEY, model="llama3-8b-8192", temperature=0),
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=False
        )
        result = qa_chain({"query": question})
        return result["result"]
    except Exception as e:
        return f"Document QA Error: {str(e)}"
