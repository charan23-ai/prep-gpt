
## Prerequisites

Ensure these are installed on your system:

*   **Ollama:** Download from [ollama.com](https://ollama.com/).
    *   Pull models: `ollama pull llama3:8b-instruct-q4_K_M` and `ollama pull all-MiniLM-L6-v2`.
    *   Run Ollama: `ollama serve` (in a separate terminal or as a service).
*   **Graphviz:** (For LangGraph visualization PNG).
    *   **macOS:** `brew install graphviz`
    *   **Windows:** Download from [graphviz.org/download/](https://graphviz.org/download/) and add to PATH.

## Setup Steps (OS Specific)

### macOS

1.  **Python Environment:**
    *   Navigate to your project root: `cd /path/to/multifunctional_doc_ai_project`
    *   Create & activate Conda env: `conda create -n rag_m4 python=3.10 -y && conda activate rag_m4`
2.  **Install Python Dependencies:**
    ```bash
    pip install Django djangorestframework django-cors-headers python-dotenv google-api-python-client pillow pypdf langchain-ollama langchain-huggingface langchain-community pygraphviz
    # If pygraphviz fails: CFLAGS="-I$(brew --prefix graphviz)/include" LDFLAGS="-L$(brew --prefix graphviz)/lib" pip install pygraphviz
    ```
3.  **Install Node.js & npm:** Download LTS version from [nodejs.org](https://nodejs.org/).
4.  **Install Node.js Dependencies:**
    *   Navigate to frontend: `cd frontend`
    *   Install: `npm install`
5.  **Configure Environment Variables:**
    *   **Backend:** Create a `.env` file in project root.
    *   **Frontend:** Create a `.env.local` file in `frontend/`.
        ```dotenv
        # .env (in project root)
        DJANGO_SECRET_KEY='your_unique_secret_key'
        LLM_MODEL="llama3:8b-instruct-q4_K_M"
        EMBEDDING_MODEL="all-MiniLM-L6-v2"
        GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE" # Optional
        GOOGLE_CSE_ID="YOUR_CUSTOM_SEARCH_ENGINE_ID_HERE" # Optional
        CUSTOM_HANDWRITING_FONT_PATH="fonts/YourHandwritingFont.ttf"

        # .env.local (in frontend/ folder)
        NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000/api/
        ```
6.  **Prepare Handwriting Font:**
    *   Create `fonts/` directory in project root: `mkdir fonts`
    *   Place your `.ttf` font file inside `fonts/`. Ensure its name matches `CUSTOM_HANDWRITING_FONT_PATH` in `.env`.
7.  **Run Django Migrations:**
    *   Navigate to project root: `cd /path/to/multifunctional_doc_ai_project`
    *   Run: `python manage.py migrate`

### Windows

1.  **Python Environment:**
    *   Navigate to your project root: `cd C:\path\to\multifunctional_doc_ai_project`
    *   Create & activate Conda env: `conda create -n rag_m4 python=3.10 -y && conda activate rag_m4`
2.  **Install Python Dependencies:**
    ```bash
    pip install Django djangorestframework django-cors-headers python-dotenv google-api-python-client pillow pypdf langchain-ollama langchain-huggingface langchain-community pygraphviz
    ```
    *(If `pygraphviz` fails, ensure Graphviz is installed and its `bin/` directory is in your System PATH. You might need to try `pip install pygraphviz --global-option=build_ext --global-option="-IC:\path\to\Graphviz\include" --global-option="-LC:\path\to\Graphviz\lib"` replacing paths, or `conda install pygraphviz -c conda-forge`.)*
3.  **Install Node.js & npm:** Download LTS version from [nodejs.org](https://nodejs.org/).
4.  **Install Node.js Dependencies:**
    *   Navigate to frontend: `cd frontend`
    *   Install: `npm install`
5.  **Configure Environment Variables:**
    *   **Backend:** Create a `.env` file in project root.
    *   **Frontend:** Create a `.env.local` file in `frontend/`.
        ```dotenv
        # .env (in project root)
        DJANGO_SECRET_KEY='your_unique_secret_key'
        LLM_MODEL="llama3:8b-instruct-q4_K_M"
        EMBEDDING_MODEL="all-MiniLM-L6-v2"
        GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE" # Optional
        GOOGLE_CSE_ID="YOUR_CUSTOM_SEARCH_ENGINE_ID_HERE" # Optional
        CUSTOM_HANDWRITING_FONT_PATH="fonts/YourHandwritingFont.ttf"

        # .env.local (in frontend/ folder)
        NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000/api/
        ```
6.  **Prepare Handwriting Font:**
    *   Create `fonts/` directory in project root: `mkdir fonts`
    *   Place your `.ttf` font file inside `fonts/`. Ensure its name matches `CUSTOM_HANDWRITING_FONT_PATH` in `.env`.
7.  **Run Django Migrations:**
    *   Navigate to project root: `cd C:\path\to\multifunctional_doc_ai_project`
    *   Run: `python manage.py migrate`

## Running the Application

1.  **Start Backend Server:**
    *   Open **Terminal/Command Prompt 1**.
    *   `conda activate rag_m4`
    *   `cd /path/to/multifunctional_doc_ai_project`
    *   `python manage.py runserver --noreload` (Keep this window open)

2.  **Start Frontend Development Server:**
    *   Open **Terminal/Command Prompt 2**.
    *   `cd /path/to/multifunctional_doc_ai_project/frontend`
    *   `npm run dev` (Keep this window open)

3.  **Access the Application:** Open your web browser to `http://localhost:3000/`.

## Key Usage Steps

1.  **Document Management:** Navigate to the "Documents" tab.
    *   **Upload** your text files (e.g., `physics_chapter.txt`, `physics_chapter2.txt`).
    *   Click **"Add Documents"**. This processes and stores them in a persistent knowledge base. (Do this once per session or when you add new files).
    *   (Optional) Click "Clear All Documents" to reset the database.

2.  **RAG Chat:** Go to the "RAG Chat" tab.
    *   Type questions related to your uploaded documents (e.g., "What is Bernoulli's principle?") or general knowledge (e.g., "Who won the Nobel Prize in Physics in 2023?").
    *   Click "Ask".

3.  **Question Generator:** Go to the "QGen" tab.
    *   Enter a **Study Topic** (e.g., "Hooke's Law"), **Number of Questions**, and **Difficulty**.
    *   Click "Generate Study Questions".

4.  **Summarizer:** Go to the "Summarizer" tab.
    *   Enter a **Topic for Summary** (e.g., "Surface Tension and Capillary Rise").
    *   (Optional) Check "Generate Handwriting Image".
    *   Click "Generate Summary Notes".
    *   Handwriting images are saved in the `media/` folder and accessible via `http://localhost:8000/media/` (e.g., `http://localhost:8000/media/summary_YourTopic_handwriting.png`).

## Troubleshooting Common Issues

*   **ChromaDB "Readonly" Errors:** Ensure `python manage.py runserver --noreload` is used. Manually delete `chroma_db_multi_app/`, `chroma_db_questions_app/`, `pdf_temp_files/`, and `media/` directories from your project root if problems persist, then restart the server.
*   **Ollama/Model Errors:** Confirm `ollama serve` is running and models are pulled.
*   **API Call Failures (404/500):** Check backend terminal for detailed Python tracebacks. Verify API endpoint URLs in frontend match Django's `urls.py`.
*   **Handwriting Font Errors:** Ensure `fonts/` directory exists in project root, your `.ttf` file is inside it, and `CUSTOM_HANDWRITING_FONT_PATH` in `.env` has the correct filename.
*   **Graphviz Errors:** Ensure `graphviz` is installed system-wide.

---

### LangGraph Workflow Visualization

A PNG image of the LangGraph workflow is saved at `media/rag_workflow.png` in your project root after Django backend startup. You can also paste the content of `media/rag_workflow.mermaid` into [Mermaid Live Editor](https://mermaid.live/) for interactive viewing.
