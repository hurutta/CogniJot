# CogniJot
AI-powered academic note-taking tool that beautifies, refines, and corrects errors in your notes.

## Description
A lightweight web application built with FastAPI that provides an interface for writing, formatting, error-checking, and exploring text. 
Users can compose and beautify text, highlight mistakes with suggestions, extract topics and keywords, perform deep searches based on the gist of their text, 
and store notes for future reference.

## High-Level Design

```mermaid
%%{
  init: {
    "theme": "base",
    "themeVariables": {
      "background": "#F2F2F2",
      "primaryColor": "#000000",
      "secondaryColor": "#EAE4D5",
      "tertiaryColor": "#B6B09F",
      "edgeLabelBackground": "#F2F2F2",
      "fontFamily": "Arial",
      "textColor": "#000000"
    }
  }
}%%
flowchart LR
%% UI Layer
subgraph UI[" "]
direction LR
Editor["Editor<br/>(User Interface)"]
end

%% Analysis Layer
subgraph Analysis[" "]
direction LR
DuckDuckGo["DuckDuckGo API<br/>(Search)"]
end

%% Analysis Layer
subgraph Analysis2[" "]
direction LR
LLM["LLM<br/>(Cloud/locally hosted)"]
end

%% Actions Layer
subgraph Actions[" "]
direction TB
GenerateButton["Generate<br/>(Format & Beautify)"]
ErrorButton["Error Finder<br/>(Find error)"]

QueryAnalysis["Query Analysis<br/>(Deep search)"]

TopicExtraction["Topic Extraction<br/>(LDA)"]

end

%% Storage Layer
subgraph Storage[" "]
direction LR
HistoryDB["History Store<br/>(TinyDB)"]
end

%% Flows
Editor -- " Store raw text" --> HistoryDB
Editor <--> TopicExtraction
Editor <--> GenerateButton

Editor <--> ErrorButton
ErrorButton --> LLM
ErrorButton --> HistoryDB

GenerateButton --> LLM
GenerateButton --> HistoryDB
QueryAnalysis -- " find query gist" --> LLM

Editor <--> QueryAnalysis

QueryAnalysis -- " LLM generated query " --> DuckDuckGo


%% Minimal Palette Styling
classDef ui      fill: #EAE4D5, stroke: #000000, stroke-width: 2px, rounded;
classDef logic   fill: #B6B09F,stroke: #000000, stroke-width: 2px, rounded;
classDef action  fill: #F2F2F2, stroke: #000000, stroke-width: 2px, rounded;
classDef api     fill:#EAE4D5, stroke: #000000, stroke-width: 2px,rounded;
classDef db      fill: #B6B09F, stroke: #000000, stroke-width: 2px, rounded;
classDef llm     fill: #B6BA9F, stroke: #000000, stroke-width:2px, rounded;


class Editor ui;
class TopicExtraction action;
class GenerateButton,ErrorButton,SearchButton,ErrorCheck,QueryAnalysis action;
class DuckDuckGo api;
class HistoryDB db;
class LLM llm;

```

## Key Features
- **Text Editor**  
  Format and beautify your text using a rich content-editable area.
- **Error Checking**  
  Automatically find errors (e.g. grammatical, mathematical etc.) and view suggestions via hover tooltips.
- **Topic & Keyword Extraction**  
  Extract up to 10 unique keywords or topics from your text as colorful tags.
- **Deep Search**  
  Perform a “deep search” by sending the gist of your text to a search engine and view curated results directly in the UI.
- **Note Storage & History**  
  Save, load, edit, and delete notes in the left-hand history panel.


## Contributing

I’d love your help! Here’s how you can get involved:

- **Report issues**: Let us know if you find any bugs or have ideas for improvements.  
- **Suggest features**: Have a new idea? Open an issue to share your thoughts.  
- **Help with documentation**: Clarify instructions, fix typos, or add examples.  
- **Submit fixes**: If you know how to solve a problem, send us a pull request.


