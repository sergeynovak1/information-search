import os

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from demo.search_engine import TFIDFVectorSearch
from demo.load_links import load_index

app = FastAPI()
engine = TFIDFVectorSearch("./hw-4/tf_idf_tokens")
index_path = "hw-5/index.json"

if os.path.exists(index_path):
    engine.load_index("hw-5")
else:
    engine.load_data()
    engine.save_index()

templates = Jinja2Templates(directory="demo/templates")

index_map = load_index("./hw-1/index.txt")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "results": None})


@app.post("/search", response_class=HTMLResponse)
def search(request: Request, query: str = Form(...)):
    relevant_docs = engine.search(query)
    urls = [index_map[res["doc_id"]] for res in relevant_docs if res["doc_id"] in index_map]


    return templates.TemplateResponse("index.html", {
        "request": request,
        "results": urls[:10],
        "query": query
    })