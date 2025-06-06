from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import random

app = FastAPI()

# ─────────────────────────────────────────────────────────────────────────────
# In‐memory storage (for demo purposes). Each index i refers to one entry.
history_list = []        # list of raw texts
processed_list = []      # parallel list of processed outputs ("" if never generated)

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
    # Embed the HTML/JS directly:
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>ChatGPT‐Style Interface (FastAPI)</title>
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
    .editor-body textarea {
      height: 150px;
      resize: vertical;
      width: 100%;
      padding: 8px;
      font-size: 14px;
      border: 1px solid #ccc;
      border-radius: 4px;
      box-sizing: border-box;
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
        <textarea id="editorTextarea" placeholder="Type your message here..."></textarea>
        <div class="editor-buttons">
          <button id="newButton" type="button">New</button>
          <button id="saveButton" type="button">Save</button>
          <button id="generateButton" type="button">Generate</button>
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
    const editorTextarea = document.getElementById("editorTextarea");
    const newButton = document.getElementById("newButton");
    const saveButton = document.getElementById("saveButton");
    const generateButton = document.getElementById("generateButton");
    const deleteButton = document.getElementById("deleteButton");
    const randomTextDiv = document.getElementById("randomText");
    const processedOutput = document.getElementById("processedOutput");

    let historyList = [];   // mirrors server‐side history_list
    let currentIndex = -1;  // selected history index, or –1 if none

    // ─── Renders left‐column history; each shows up to 20 chars + “...” ───────
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
          editorTextarea.value = historyList[idx];
          // After loading the text, fetch its stored processed output:
          fetch(`/processed?index=${idx}`)
            .then(res => res.json())
            .then(data => {
              processedOutput.textContent = data.processed;
            })
            .catch(console.error);
          renderHistory();
        });
        historyUl.appendChild(li);
      });
    }

    // ─── “New”: clear editor, clear processed, and deselect history ───────────
    newButton.addEventListener("click", () => {
      currentIndex = -1;
      editorTextarea.value = "";
      processedOutput.textContent = "";
      renderHistory();
      editorTextarea.focus();
    });

    // ─── “Save”: POST /save (index,text) → returns updated history & index;
    //     then immediately call /process to generate + display the processed text ─
    saveButton.addEventListener("click", () => {
      const text = editorTextarea.value.trim();
      if (!text) return;
      fetch("/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ index: currentIndex, text: text })
      })
      .then(res => res.json())
      .then(data => {
        historyList = data.history;
        currentIndex = data.index;
        renderHistory();
        // Now, call /process to generate processed text for this index:
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

    // ─── “Generate”: POST /process (index,text) → returns processed & stores it ─
    generateButton.addEventListener("click", () => {
      const text = editorTextarea.value;
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

    // ─── “Delete”: POST /delete(index) → returns updated history ───────────────
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
        currentIndex = -1;
        editorTextarea.value = "";
        processedOutput.textContent = "";
        renderHistory();
      })
      .catch(console.error);
    });

    // ─── Every second: GET /random → display in right column ─────────────────
    function fetchRandom() {
      fetch("/random")
        .then(res => res.json())
        .then(data => {
          randomTextDiv.textContent = data.random;
        })
        .catch(console.error);
    }
    setInterval(fetchRandom, 1000);
    fetchRandom();  // initial call

    // ─── On page load: GET /history → populate left panel ────────────────────
    window.addEventListener("DOMContentLoaded", () => {
      fetch("/history")
        .then(res => res.json())
        .then(data => {
          historyList = data.history;
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
    """Returns one random string each time JS calls this endpoint."""
    return JSONResponse({"random": random.choice(SAMPLE_TEXTS)})


@app.get("/history")
async def get_history():
    """
    Returns the current in‐memory history_list so the front‐end can render it.
    """
    return JSONResponse({"history": history_list})


@app.post("/save")
async def save_entry(request: Request):
    """
    Called when user clicks “Save”.
    Expects JSON: { "index": <idx_or_-1>, "text": "<content>" }.
    If index >= 0, overwrite history_list[index]; otherwise append new.
    Also keep processed_list aligned (initialize new or reset if overwritten).
    Returns: { "history": history_list, "index": new_or_updated_index }.
    """
    data = await request.json()
    idx = data.get("index", -1)
    text = data.get("text", "").strip()
    if not text:
        return JSONResponse({"history": history_list, "index": idx})

    if 0 <= idx < len(history_list):
        # Overwrite existing entry
        history_list[idx] = text
        processed_list[idx] = ""  # reset processed, since the text changed
        new_idx = idx
    else:
        # Append new entry
        history_list.append(text)
        processed_list.append("")  # no processed yet
        new_idx = len(history_list) - 1

    return JSONResponse({"history": history_list, "index": new_idx})


@app.post("/delete")
async def delete_entry(request: Request):
    """
    Called when user clicks “Delete”.
    Expects JSON: { "index": <idx> }. Removes that entry if valid.
    Returns: { "history": history_list }.
    """
    data = await request.json()
    idx = data.get("index", -1)
    if 0 <= idx < len(history_list):
        history_list.pop(idx)
        processed_list.pop(idx)
    return JSONResponse({"history": history_list})


@app.post("/process")
async def process_input(request: Request):
    """
    Called when user clicks “Generate” or immediately after “Save”.
    Expects JSON: { "index": <idx_or_-1>, "text": "<content>" }.
    If index >= 0, store processed in processed_list[index]; else do not store.
    Returns JSON: { "processed": <the_processed_output> }.
    """
    data = await request.json()
    idx = data.get("index", -1)
    text = data.get("text", "")

    # Example processing: uppercase. Replace with any Python logic you need.
    processed = text.upper()

    if 0 <= idx < len(processed_list):
        processed_list[idx] = processed

    return JSONResponse({"processed": processed})


@app.get("/processed")
async def get_processed(index: int):
    """
    Returns the stored processed output for a given history index.
    Expects query parameter ?index=<idx>.
    """
    if 0 <= index < len(processed_list):
        return JSONResponse({"processed": processed_list[index]})
    return JSONResponse({"processed": ""})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
