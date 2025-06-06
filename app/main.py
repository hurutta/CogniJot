from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import random

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
  <title>ChatGPT‐Style Interface with Error Checking</title>
  <style>
    /*─────────────────────────────────────────────────────────────────────────*/
    body, html {
      margin: 0;
      padding: 0;
      height: 100%;
      font-family: Arial, sans-serif;
    }
    .container {
      display: flex;
      height: 100vh;
    }

    /* Left: History panel (fixed 250px) */
    .history-panel {
      flex: 0 0 250px;
      border-right: 1px solid #ccc;
      display: flex;
      flex-direction: column;
      background-color: #fafafa;
    }
    .history-header {
      padding: 12px;
      border-bottom: 1px solid #ccc;
      font-weight: bold;
    }
    .history-list {
      flex: 1;
      overflow-y: auto;
      padding: 0;
      margin: 0;
      list-style: none;
    }
    .history-list li {
      padding: 8px 12px;
      cursor: pointer;
      border-bottom: 1px solid #eee;
      word-break: break-word;
    }
    .history-list li.selected {
      background-color: #e6f0ff;
    }

    /* Middle: Editor panel */
    .editor-panel {
      flex: 1;
      display: flex;
      flex-direction: column;
    }
    .editor-header {
      padding: 12px;
      border-bottom: 1px solid #ccc;
      background-color: #fafafa;
      font-weight: bold;
    }
    .editor-body {
      padding: 12px;
      display: flex;
      flex-direction: column;
    }
    /* contenteditable div styled like a textarea */
    #editorDiv {
      height: 150px;
      padding: 8px;
      font-size: 14px;
      border: 1px solid #ccc;
      border-radius: 4px;
      box-sizing: border-box;
      overflow-y: auto;
      white-space: pre-wrap;
    }
    /* Highlighted error */
    .error-highlight {
      background-color: rgba(255, 0, 0, 0.3);
      position: relative;
    }
    .error-highlight[data-error] {
      cursor: help;
    }
    .error-highlight:hover::after {
      content: attr(data-error);
      position: absolute;
      background: #333;
      color: #fff;
      padding: 4px 6px;
      border-radius: 4px;
      top: 100%;
      left: 0;
      white-space: nowrap;
      z-index: 10;
      margin-top: 2px;
      font-size: 12px;
    }
    .editor-buttons {
      margin-top: 12px;
      display: flex;
      gap: 8px;
    }
    .editor-buttons button {
      padding: 8px 16px;
      font-size: 14px;
      cursor: pointer;
      border: none;
      border-radius: 4px;
      background-color: #007bff;
      color: white;
    }
    .editor-buttons button:hover {
      background-color: #0056b3;
    }
    /* Processed‐output section with border */
    .processed-container {
      margin-top: 12px;
      padding: 12px;
      border: 1px solid #ccc;
      border-radius: 4px;
      background-color: #f9f9f9;
      min-height: 60px;
      box-sizing: border-box;
    }
    .processed-output {
      font-size: 14px;
      color: #333;
      white-space: pre-wrap;  /* preserve line breaks */
    }

    /* Right: Random text panel (fixed 250px) */
    .random-panel {
      flex: 0 0 250px;
      border-left: 1px solid #ccc;
      display: flex;
      flex-direction: column;
      background-color: #fafafa;
    }
    .random-header {
      padding: 12px;
      border-bottom: 1px solid #ccc;
      font-weight: bold;
    }
    .random-body {
      flex: 1;
      padding: 12px;
      font-size: 14px;
      overflow-y: auto;
      word-break: break-word;
    }
    /*─────────────────────────────────────────────────────────────────────────*/
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
          <button id="newButton" type="button">New</button>
          <button id="saveButton" type="button">Save</button>
          <button id="generateButton" type="button">Generate</button>
          <button id="checkErrorsButton" type="button">Check Errors</button>
          <button id="deleteButton" type="button">Delete</button>
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
    </div>
  </div>

  <script>
    // ─── DOM references ─────────────────────────────────────────────────────────
    const historyUl = document.getElementById("historyList");
    const editorDiv = document.getElementById("editorDiv");
    const newButton = document.getElementById("newButton");
    const saveButton = document.getElementById("saveButton");
    const generateButton = document.getElementById("generateButton");
    const checkErrorsButton = document.getElementById("checkErrorsButton");
    const deleteButton = document.getElementById("deleteButton");
    const randomTextDiv = document.getElementById("randomText");
    const processedOutput = document.getElementById("processedOutput");

    let historyList = [];
    let processedList = [];
    let currentIndex = -1;
    let errorWords = [];

    // Utility: escape HTML
    function escapeHTML(str) {
      return str.replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#39;");
    }

    // Renders left‐column history; show first 20 chars + “...” if longer
    function renderHistory() {
      historyUl.innerHTML = "";
      historyList.forEach((text, idx) => {
        const li = document.createElement("li");
        const displayText = text.length > 20 ? text.slice(0, 20) + "..." : text;
        li.textContent = displayText;
        li.dataset.index = idx;
        if (idx === currentIndex) li.classList.add("selected");
        li.addEventListener("click", () => {
          currentIndex = idx;
          loadHistoryItem(idx);
          renderHistory();
        });
        historyUl.appendChild(li);
      });
    }

    // Load a history item (index) into the editor & processed output
    function loadHistoryItem(idx) {
      const raw = historyList[idx];
      editorDiv.innerText = raw;
      fetch(`/processed?index=${idx}`)
        .then(res => res.json())
        .then(data => {
          processedOutput.textContent = data.processed;
        })
        .catch(console.error);
      errorWords = [];
    }

    // “New”: clear editor, processed, and deselect history
    newButton.addEventListener("click", () => {
      currentIndex = -1;
      editorDiv.innerText = "";
      processedOutput.textContent = "";
      errorWords = [];
      renderHistory();
      editorDiv.focus();
    });

    // “Save”: POST /save → then POST /process → display processed
    saveButton.addEventListener("click", () => {
      const text = editorDiv.innerText.trim();
      if (!text) return;
      fetch("/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ index: currentIndex, text: text })
      })
      .then(res => res.json())
      .then(data => {
        historyList = data.history;
        // Ensure processedList aligns (might reset)
        processedList = data.history.map((_, i) => processedList[i] || "");
        currentIndex = data.index;
        renderHistory();
        return fetch("/process", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ index: currentIndex, text: text })
        });
      })
      .then(res => res.json())
      .then(data => {
        processedOutput.textContent = data.processed;
      })
      .catch(console.error);
    });

    // “Generate”: POST /process → display processed (no history change)
    generateButton.addEventListener("click", () => {
      const text = editorDiv.innerText;
      fetch("/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ index: currentIndex, text: text })
      })
      .then(res => res.json())
      .then(data => {
        processedOutput.textContent = data.processed;
      })
      .catch(console.error);
    });

    // “Check Errors”: POST /check → highlight errors
    checkErrorsButton.addEventListener("click", () => {
      const text = editorDiv.innerText;
      fetch("/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
      })
      .then(res => res.json())
      .then(data => {
        errorWords = data.errors.map(e => e.word);
        highlightErrors(data.errors);
      })
      .catch(console.error);
    });

    // Wrap error words in <span> without resetting caret
    function highlightErrors(errors) {
      let raw = editorDiv.innerText;
      let html = escapeHTML(raw);
      // Sort unique error words by descending length
      const unique = [...new Set(errors.map(e => e.word))].sort((a, b) => b.length - a.length);
      unique.forEach(word => {
        const regex = new RegExp(escapeRegExp(word), "gi");
        html = html.replace(regex, match => {
          const errObj = errors.find(e => e.word.toLowerCase() === match.toLowerCase());
          const msg = errObj ? errObj.message : "Error";
          return `<span class="error-highlight" data-error="${escapeHTML(msg)}">${escapeHTML(match)}</span>`;
        });
      });
      editorDiv.innerHTML = html;
    }

    function escapeRegExp(str) {
      return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }

    // On input: unwrap any spans whose word no longer exists
    editorDiv.addEventListener("input", () => {
      if (errorWords.length === 0) return;
      const spans = Array.from(editorDiv.querySelectorAll("span.error-highlight"));
      spans.forEach(span => {
        const word = span.innerText;
        if (!editorDiv.innerText.includes(word)) {
          const textNode = document.createTextNode(span.innerText);
          span.parentNode.replaceChild(textNode, span);
        }
      });
    });

    // “Delete”: POST /delete → update history, clear editor/processed
    deleteButton.addEventListener("click", () => {
      if (currentIndex < 0 || currentIndex >= historyList.length) return;
      fetch("/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ index: currentIndex })
      })
      .then(res => res.json())
      .then(data => {
        historyList = data.history;
        processedList.pop(currentIndex);
        currentIndex = -1;
        editorDiv.innerText = "";
        processedOutput.textContent = "";
        errorWords = [];
        renderHistory();
      })
      .catch(console.error);
    });

    // Every second: GET /random → display in right column
    function fetchRandom() {
      fetch("/random")
        .then(res => res.json())
        .then(data => { randomTextDiv.textContent = data.random; })
        .catch(console.error);
    }
    setInterval(fetchRandom, 1000);
    fetchRandom();

    // On page load: GET /history → populate left panel
    window.addEventListener("DOMContentLoaded", () => {
      fetch("/history")
        .then(res => res.json())
        .then(data => {
          historyList = data.history;
          processedList = historyList.map(() => "");
          renderHistory();
        })
        .catch(console.error);
    });
  </script>
</body>
</html>
    """)


@app.get("/random")
async def random_text():
    return JSONResponse({"random": random.choice(SAMPLE_TEXTS)})


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
