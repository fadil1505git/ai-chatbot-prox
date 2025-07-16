from llama_index.core import Document, VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from web_scraper import fetch_web_content

def get_query_engine():
    # Load PDF
    pdf_documents = SimpleDirectoryReader("pdfs").load_data()
    
    # Fetch web content
    url = "https://www.example.com"
    web_text = fetch_web_content(url)
    web_document = Document(text=web_text)
    
    # Gabungkan semua dokumen
    all_documents = pdf_documents + [web_document]
    
    llm = Ollama(model="llama3")
    index = VectorStoreIndex.from_documents(all_documents)
    return index.as_query_engine(llm=llm)
