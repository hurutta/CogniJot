from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import random
import re

app = FastAPI()

# ─────────────────────────────────────────────────────────────────────────────
history_list = []
processed_list = []
ERROR_WORDS = ["abc", "def"]

SAMPLE_TEXTS = [
    "Lorem ipsum dolor sit amet.",
    "Consectetur adipiscing elit.",
    "Sed do eiusmod tempor incididunt.",
    "Ut labore et dolore magna aliqua.",
    "Ut enim ad minim veniam.",
    "Quis nostrud exercitation ullamco.",
    "Laboris nisi ut aliquip ex ea commodo consequat.",
    "Duis aute irure dolor in reprehenderit.",
    "In voluptate velit esse cillum dolore.",
    "Eu fugiat nulla pariatur."
]
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>ChatGPT‐Style Interface</title>
  <style>
    body, html { margin:0; padding:0; height:100%; font-family:Arial,sans-serif; }
    .container { display:flex; height:100vh; }

    .history-panel { flex:0 0 250px; border-right:1px solid #ccc; display:flex; flex-direction:column; background:#fafafa; }
    .history-header { padding:12px; border-bottom:1px solid #ccc; font-weight:bold; }
    .history-list { flex:1; overflow-y:auto; padding:0; margin:0; list-style:none; }
    .history-list li { padding:8px 12px; cursor:pointer; border-bottom:1px solid #eee; word-break:break-word; }
    .history-list li.selected { background:#e6f0ff; }

    .editor-panel { flex:1; display:flex; flex-direction:column; }
    .editor-header { padding:12px; border-bottom:1px solid #ccc; background:#fafafa; font-weight:bold; }
    .editor-body { padding:12px; display:flex; flex-direction:column; }
    #editorDiv { height:150px; padding:8px; font-size:14px; border:1px solid #ccc; border-radius:4px; box-sizing:border-box; overflow-y:auto; white-space:pre-wrap; }
    .editor-buttons { margin-top:12px; display:flex; gap:8px; }
    .editor-buttons button { padding:8px 16px; font-size:14px; cursor:pointer; border:none; border-radius:4px; background:#007bff; color:#fff; }
    .editor-buttons button:hover { background:#0056b3; }
    .processed-container { margin-top:12px; padding:12px; border:1px solid #ccc; border-radius:4px; background:#f9f9f9; min-height:60px; box-sizing:border-box; }
    .processed-output { font-size:14px; color:#333; white-space:pre-wrap; }

    .random-panel { flex:0 0 350px; border-left:1px solid #ccc; display:flex; flex-direction:column; background:#fafafa; }
    .random-header { padding:12px; border-bottom:1px solid #ccc; font-weight:bold; }
    .random-body { flex:1; padding:12px; font-size:14px; overflow-y:auto; word-break:break-word; }
    .tag { display:inline-block; padding:4px 8px; margin:2px; border-radius:4px; font-size:12px; background:#e0f7fa; color:#333; }

    .search-button { margin:12px; padding:8px 16px; font-size:14px; cursor:pointer; border:none; border-radius:4px; background:#28a745; color:#fff; }
    .search-button:hover { background:#1e7e34; }
    .search-container { flex:1.5; margin:12px; padding:12px; border:1px solid #ccc; border-radius:4px; background:#fff; overflow-y:auto; box-sizing:border-box; }
    .search-list { list-style:none; padding:0; margin:0; }
    .search-list li { display:flex; align-items:center; padding:4px 0; border-bottom:1px solid #eee; }
    .search-list img { width:40px; height:40px; object-fit:cover; margin-right:8px; }
    .search-list a { font-weight:bold; color:#007bff; text-decoration:none; margin-right:8px; }
    .search-list p { margin:0; font-size:12px; color:#555; }

    .error-highlight { background:rgba(255,0,0,0.3); position:relative; }
    .error-highlight[data-error]:hover::after {
      content:attr(data-error); position:absolute; background:#333; color:#fff;
      padding:4px 6px; border-radius:4px; top:100%; left:0; white-space:nowrap; z-index:10; margin-top:2px; font-size:12px;
    }
  </style>
</head>
<body>
  <div class="container">
    <!-- Left: History Panel -->
    <div class="history-panel">
      <div class="history-header">History</div>
      <ul id="historyList" class="history-list"></ul>
    </div>

    <!-- Middle: Editor Panel -->
    <div class="editor-panel">
      <div class="editor-header">Text Editor</div>
      <div class="editor-body">
        <div id="editorDiv" contenteditable="true"></div>
        <div class="editor-buttons">
          <button id="newButton">New</button>
          <button id="saveButton">Save</button>
          <button id="generateButton">Generate</button>
          <button id="checkErrorsButton">Check Errors</button>
          <button id="deleteButton">Delete</button>
        </div>
        <div class="processed-container">
          <div><strong>Processed Output:</strong></div>
          <div id="processedOutput" class="processed-output"></div>
        </div>
      </div>
    </div>

    <!-- Right: Random Text Panel -->
    <div class="random-panel">
      <div class="random-header">Random Text</div>
      <div id="randomText" class="random-body"></div>

      <button id="searchButton" class="search-button">Search</button>

      <div class="search-container">
        <div><strong>Search Results:</strong></div>
        <ul id="searchResults" class="search-list"></ul>
      </div>
    </div>
  </div>

  <script>
    const historyUl      = document.getElementById("historyList");
    const editorDiv      = document.getElementById("editorDiv");
    const newButton      = document.getElementById("newButton");
    const saveButton     = document.getElementById("saveButton");
    const generateButton = document.getElementById("generateButton");
    const checkErrorsBtn = document.getElementById("checkErrorsButton");
    const deleteButton   = document.getElementById("deleteButton");
    const randomTextDiv  = document.getElementById("randomText");
    const processedOutput= document.getElementById("processedOutput");
    const searchButton   = document.getElementById("searchButton");
    const searchResults  = document.getElementById("searchResults");

    let historyArr   = [], processedArr = [], currentIndex = -1, errorWords = [];

    function escapeHTML(s) {
      return s.replace(/&/g,"&amp;").replace(/</g,"&lt;")
              .replace(/>/g,"&gt;").replace(/"/g,"&quot;")
              .replace(/'/g,"&#39;");
    }

    function renderHistory() {
      historyUl.innerHTML = "";
      historyArr.forEach((t,i)=>{
        const li = document.createElement("li");
        li.textContent = t.length>20 ? t.slice(0,20)+"..." : t;
        li.dataset.index = i;
        if (i===currentIndex) li.classList.add("selected");
        li.addEventListener("click", () => {
          currentIndex = i;
          loadHistory(i);
          renderHistory();
        });
        historyUl.appendChild(li);
      });
    }

    function loadHistory(i) {
      editorDiv.innerText = historyArr[i];
      fetch(`/processed?index=${i}`)
        .then(r=>r.json())
        .then(d=> processedOutput.textContent = d.processed);
      errorWords = [];
      // **Fetch random tags upon toggling history**
      fetchRandom();
    }

    newButton.onclick = () => {
      currentIndex=-1; editorDiv.innerText=""; processedOutput.textContent="";
      errorWords=[]; renderHistory(); editorDiv.focus();
    };

    saveButton.onclick = () => {
      const text = editorDiv.innerText.trim();
      if(!text) return;
      fetch("/save", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({index:currentIndex, text})
      })
      .then(r=>r.json())
      .then(d=>{
        historyArr = d.history;
        processedArr = historyArr.map((_,i)=>processedArr[i]||"");
        currentIndex = d.index;
        renderHistory();
        return fetch("/process", {
          method:"POST", headers:{"Content-Type":"application/json"},
          body:JSON.stringify({index:currentIndex, text})
        });
      })
      .then(r=>r.json())
      .then(d=> processedOutput.textContent = d.processed)
      .catch(console.error);
    };

    generateButton.onclick = () => {
      const text=editorDiv.innerText;
      fetch("/process", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({index:currentIndex, text})
      })
      .then(r=>r.json())
      .then(d=> processedOutput.textContent = d.processed)
      .catch(console.error);
    };

    checkErrorsBtn.onclick = () => {
      const txt = editorDiv.innerText;
      fetch("/check", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({text:txt})
      })
      .then(r=>r.json())
      .then(d=>{
        errorWords = d.errors.map(e=>e.word);
        highlightErrors(d.errors);
      })
      .catch(console.error);
    };

    function highlightErrors(errors) {
      let raw = editorDiv.innerText, html=escapeHTML(raw);
      const uniq=[...new Set(errors.map(e=>e.word))].sort((a,b)=>b.length-a.length);
      uniq.forEach(w=>{
        const rx=new RegExp(escapeRegExp(w),"gi");
        html=html.replace(rx,m=>{
          const msg=errors.find(e=>e.word.toLowerCase()===m.toLowerCase()).message;
          return `<span class="error-highlight" data-error="${escapeHTML(msg)}">${escapeHTML(m)}</span>`;
        });
      });
      editorDiv.innerHTML=html;
    }
    function escapeRegExp(s){ return s.replace(/[.*+?^${}()|[\]\\]/g,"\\$&"); }

    // **Use addEventListener for delete to ensure it registers**
    deleteButton.addEventListener("click", () => {
      if(currentIndex<0||currentIndex>=historyArr.length) return;
      fetch("/delete", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({index:currentIndex})
      })
      .then(r=>r.json())
      .then(d=>{
        historyArr = d.history;
        processedArr.pop(currentIndex);
        currentIndex = -1;
        editorDiv.innerText = "";
        processedOutput.textContent = "";
        errorWords = [];
        renderHistory();
      })
      .catch(console.error);
    });

    // **Debounce random fetch on pause (5s)**
    let randomTimeout;
    function fetchRandom() {
      const txt = editorDiv.innerText||"";
      fetch("/random", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({text:txt})
      })
      .then(r=>r.json())
      .then(d=>{
        randomTextDiv.innerHTML = "";
        d.tags.forEach(tag=>{
          const sp = document.createElement("span");
          sp.className = "tag"; sp.textContent = tag;
          randomTextDiv.appendChild(sp);
        });
      })
      .catch(console.error);
    }
    editorDiv.addEventListener("input", () => {
      clearTimeout(randomTimeout);
      randomTimeout = setTimeout(fetchRandom, 5000);
      // unwrap error spans if deleted
      if(errorWords.length){
        Array.from(editorDiv.querySelectorAll("span.error-highlight")).forEach(span=>{
          const w = span.innerText;
          if(!editorDiv.innerText.includes(w)){
            span.parentNode.replaceChild(document.createTextNode(w), span);
          }
        });
      }
    });

    // **Search uses editor content**
    searchButton.addEventListener("click", () => {
      const q = editorDiv.innerText.trim().toLowerCase();
      fetch("/search", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({query:q})
      })
      .then(r=>r.json())
      .then(data=>{
        searchResults.innerHTML = "";
        (data.results||[]).forEach(item=>{
          const li = document.createElement("li");
          const img = document.createElement("img"); img.src=item.logo;
          const a = document.createElement("a"); a.href=item.link; a.target="_blank"; a.textContent=item.title;
          const p = document.createElement("p"); p.textContent=item.description;
          li.appendChild(img); li.appendChild(a); li.appendChild(p);
          searchResults.appendChild(li);
        });
        if(!(data.results||[]).length){
          const li = document.createElement("li");
          li.textContent = "No results found.";
          searchResults.appendChild(li);
        }
      })
      .catch(console.error);
    });

    window.addEventListener("DOMContentLoaded", () => {
      fetch("/history")
        .then(r=>r.json())
        .then(d=>{
          historyArr = d.history;
          processedArr = historyArr.map(()=> "");
          renderHistory();
          fetchRandom();  // initial tags load
        })
        .catch(console.error);
    });
  </script>
</body>
</html>
    """)


@app.post("/random")
async def random_text(request: Request):
    data = await request.json()
    text = data.get("text", "")
    words = re.findall(r"\b\w+\b", text)
    unique = []
    for w in words:
        lw = w.lower()
        if lw not in unique and len(lw) > 2:
            unique.append(lw)
        if len(unique) >= 10:
            break
    return JSONResponse({"tags": unique})


@app.post("/search")
async def search_endpoint(request: Request):
    dummy = [
        {
            "title": "FastAPI v0.95 Released",
            "description": "FastAPI 0.95 brings performance improvements and new features.",
            "logo": "https://via.placeholder.com/40",
            "link": "https://fastapi.tiangolo.com/"
        },
        {
            "title": "Gradio 4.0 Launched",
            "description": "Gradio 4.0 introduces a revamped UI and faster load times.",
            "logo": "https://via.placeholder.com/40",
            "link": "https://gradio.app/"
        }
    ]
    return JSONResponse({"results": dummy})


@app.get("/history")
async def get_history():
    return JSONResponse({"history": history_list})


@app.post("/save")
async def save_entry(request: Request):
    data = await request.json()
    idx = data.get("index", -1)
    text = data.get("text", "").strip()
    if not text:
        return JSONResponse({"history": history_list, "index": idx})

    if 0 <= idx < len(history_list):
        history_list[idx] = text
        processed_list[idx] = ""
        new_idx = idx
    else:
        history_list.append(text)
        processed_list.append("")
        new_idx = len(history_list) - 1

    return JSONResponse({"history": history_list, "index": new_idx})


@app.post("/delete")
async def delete_entry(request: Request):
    data = await request.json()
    idx = data.get("index", -1)
    if 0 <= idx < len(history_list):
        history_list.pop(idx)
        processed_list.pop(idx)
    return JSONResponse({"history": history_list})


@app.post("/process")
async def process_input(request: Request):
    data = await request.json()
    idx = data.get("index", -1)
    text = data.get("text", "")

    processed = text.upper()

    if 0 <= idx < len(processed_list):
        processed_list[idx] = processed

    return JSONResponse({"processed": processed})


@app.get("/processed")
async def get_processed(index: int):
    if 0 <= index < len(processed_list):
        return JSONResponse({"processed": processed_list[index]})
    return JSONResponse({"processed": ""})


@app.post("/check")
async def check_errors(request: Request):
    data = await request.json()
    text = data.get("text", "").lower()
    errors = []
    for word in ERROR_WORDS:
        if word in text:
            errors.append({"word": word, "message": f"'{word}' is an error"})
    return JSONResponse({"errors": errors})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
