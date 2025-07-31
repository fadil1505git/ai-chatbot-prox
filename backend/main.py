from fastapi import FastAPI, Query, BackgroundTasks, UploadFile, File, Form, Request
from chat_engine import get_query_engine, clear_index_cache
from pathlib import Path
import shutil
import time
import json

app = FastAPI()

@app.get("/ask")
def ask(
    q: str = Query(..., description="Soalan pengguna"),
    model: str = Query("qwen2:1.5b", description="Model LLM")
):
    with open("queries.log", "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {q} ({model})\n")
    engine = get_query_engine(model)
    response = engine.query(q)
    return {"answer": str(response)}

@app.post("/reload")
def reload_index(background_tasks: BackgroundTasks):
    background_tasks.add_task(reload)
    return {"status": "Reloading index..."}

def reload():
    clear_index_cache()

@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    file_path = Path("pdfs") / file.filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": f"Uploaded {file.filename}"}

@app.get("/logs")
def get_logs():
    try:
        with open("queries.log") as f:
            return f.read()
    except FileNotFoundError:
        return "Log kosong."

@app.post("/admin/set_urls")
def set_urls(urls: str = Form(...)):
    with open("urls.txt", "w") as f:
        f.write(urls)
    clear_index_cache()
    return {"status": "URL disimpan."}

@app.post("/add_url")
async def add_url(request: Request):
    try:
        data = await request.json()
        url = data.get("url")
        if not url:
            return {"error": "URL tidak sah"}
        with open("urls.txt", "a") as f:
            f.write(url.strip() + "\n")
        clear_index_cache()
        return {"status": f"URL '{url}' berjaya ditambah"}
    except Exception as e:
        return {"error": str(e)}
