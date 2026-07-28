# Recipe Saver Chrome Extension

A lightweight Chrome extension that saves recipes from supported websites into structured JSON files on the local machine.

Instead of bookmarking recipes or copying them into notes, this project extracts recipe information directly from the webpage, parses it into structured data, and stores it locally for future use.

---

## Features

* Save a recipe from a web page with one click
* Parse recipes into structured JSON
* Store recipes locally
* Designed for easy searching and future AI processing
* Built primarily in Python

---

## Architecture

```
Chrome Extension
    │
    ▼
Reads current webpage
    │
    ▼
Sends HTML + URL
    │
HTTP POST
    │
    ▼
FastAPI Backend
    │
    ▼
Recipe Parser
    │
    ▼
Local JSON Storage
```

The Chrome extension is intentionally lightweight. Nearly all of the parsing and storage logic lives in the Python backend.

---

## Project Structure

```
recipe-scraper/
├── extension/
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   ├── background.js
│   └── content.js
├── backend/
│   ├── main.py
│   ├── parser.py
│   ├── storage.py
│   └── models.py
├── recipes/
└── README.md
```

---

## Components

### Chrome Extension

The extension provides a button in the popup UI. When clicked, it queries the active tab and sends a message to the content script.

The content script then sends a POST request to:

```text
http://localhost:8000/save
```

with:

- the current page URL
- the page HTML

### FastAPI Backend

The backend exposes a POST endpoint in [backend/main.py](backend/main.py) that receives the request and routes it to the parser.

### Recipe Parser

The parser in [backend/parser.py](backend/parser.py) uses:

- recipe_scrapers to extract recipe data from HTML
- ingredient_parser to parse ingredient strings into structured fields

It returns a recipe object with:

- title
- ingredients
- instructions
- total_time
- yields
- image
- source

### Storage

The storage layer in [backend/storage.py](backend/storage.py) writes each recipe as a JSON file into the recipes folder. The current filename format is based on the recipe title.

---

## Example Output

```json
{
  "title": "Easy Tiramisu",
  "ingredients": [
    {
      "quantity": "8",
      "unit": "oz",
      "name": "mascarpone"
    }
  ],
  "instructions": [
    "Whisk the egg yolks.",
    "Fold in the mascarpone."
  ],
  "total_time": 30,
  "yields": "8 servings",
  "image": "https://example.com/image.jpg",
  "source": "https://example.com/recipe"
}
```

---

## Setup

#### 1. Install Python dependencies

```bash
pip install fastapi uvicorn recipe-scrapers ingredient-parser-nlp
```

#### 2. Start the backend

```bash
cd backend
uvicorn main:app --reload
```

The server will start on:

```
http://localhost:8000
```

#### 3. Load the Chrome extension

1. Open Chrome and go to chrome://extensions
2. Enable Developer Mode
3. Click Load unpacked
4. Select the extension folder from this repository

#### 4. Save a recipe

Open a supported recipe page, click the extension icon, and choose Save Recipe.

---

## Current implementation notes

- The project currently focuses on local storage rather than a database or cloud sync
- Parsing quality depends on how well the target site is supported by recipe_scrapers
- Ingredient parsing is currently basic and may need improvement for edge cases
