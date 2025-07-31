from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Document
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.prompts import PromptTemplate
#from llama_index.core.response.pydantic import Response
#from llama_index.core.response.schema import RESPONSE_TYPE
#from llama_index.core.response_synthesizers import ResponseSynthesizer
#from llama_index.core.retrievers import VectorIndexRetriever
import requests
from bs4 import BeautifulSoup

query_engine_cache = {}

def load_web_documents(url_file="urls.txt"):
    documents = []
    try:
        with open(url_file, "r") as f:
            urls = [line.strip() for line in f if line.strip()]
        for url in urls:
            try:
                print(f"Fetching: {url}")
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                for script in soup(["script", "style", "noscript"]): script.decompose()
                text = soup.get_text(separator="\n")
                cleaned_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
                if cleaned_text:
                    documents.append(Document(text=cleaned_text))
                    print(f"? Fetched {url} ({len(cleaned_text)} chars)")
                else:
                    print(f"?? Kosong selepas dibersihkan: {url}")
            except Exception as e:
                print(f"? Gagal muat {url}: {e}")
    except FileNotFoundError:
        print("?? Fail urls.txt tidak dijumpai.")
    print(f"Jumlah laman web berjaya dimuatkan: {len(documents)}")
    return documents

def build_index(model: str = "qwen2:1.5b"):
    print("?? Membina index dengan model:", model)

    # Muatkan dokumen PDF
    pdf_documents = SimpleDirectoryReader("pdfs").load_data()
    print(f"? {len(pdf_documents)} dokumen PDF dimuatkan.")

    # Muatkan kandungan web
    web_documents = load_web_documents()

    # Gabungkan dokumen
    all_documents = pdf_documents + web_documents
    #all_documents = web_documents
    if not all_documents:
        print("? Tiada dokumen dimuatkan. Sila semak folder pdfs/ atau fail urls.txt.")

    # Tetapkan LLM dan embedding
    llm = Ollama(model="qwen2:1.5b", base_url="http://ollama:11434", request_timeout=120)
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # Bina index
    index = VectorStoreIndex.from_documents(all_documents, embed_model=embed_model)

    # Template jawapan
    qa_prompt = PromptTemplate(
        "Jawab hanya berdasarkan maklumat di bawah. "
        "Jika tiada maklumat relevan, katakan 'Maaf, saya tidak menemui jawapan dalam sumber yang diberikan.'\n\n"
        "{context_str}\n\nSoalan: {query_str}\nJawapan:"
    )

    retriever = index.as_retriever(similarity_top_k=3)

    query_engine = RetrieverQueryEngine.from_args(
        retriever=index.as_retriever(),
        llm=llm,
        response_mode="compact",
        text_qa_template=qa_prompt
    )

    print("? Index berjaya dibina.")
    return query_engine

def get_query_engine(model: str = "qwen2:1.5b"):
    if model not in query_engine_cache:
        query_engine_cache[model] = build_index(model)
    return query_engine_cache[model]

def clear_index_cache():
    print("?? Cache index dibersihkan.")
    query_engine_cache.clear()
