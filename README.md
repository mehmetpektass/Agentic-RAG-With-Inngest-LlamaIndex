# 📄 Enterprise AI Document Assistant (Event-Driven RAG)



## 💻 Description
This project is a modern, **Event-Driven RAG (Retrieval-Augmented Generation)** application designed to analyze large PDF documents, summarize content, and perform Q&A with high accuracy.

Unlike standard RAG applications, this project utilizes **Inngest** for orchestration, making data ingestion and processing workflows asynchronous, durable, and fault-tolerant. It leverages **`uv`** for lightning-fast dependency management.

<br>

## 🚀 Features

* **Event-Driven Architecture:** Asynchronous background jobs managed by Inngest (Retries, Step functions, Flow control).
* **High-Performance Vector Search:** Semantic search powered by Qdrant.
* **Hybrid AI Models:**
    * **LLM:** Groq (Llama-3-70b/8b) for ultra-fast inference.
    * **Embedding:** Cohere Multilingual v3 for high-accuracy vectorization.
* **Modern UI:** Professional, "Dashboard-style" Streamlit interface with dark/light mode support.
* **Modern Tooling:** Built with `uv` for robust package management.

<br>

## 🛠️ Tech Stack

* **Language:** Python 3.12+
* **Orchestration:** Inngest (Serverless Queue & Workflow)
* **Backend:** FastAPI
* **Vector Database:** Qdrant (Local Docker or Cloud)
* **Data Framework:** LlamaIndex
* **LLM Provider:** Groq API
* **Embedding:** Cohere API
* **Frontend:** Streamlit
* **Package Manager:** uv (Astral)

<br>

## 📂 Project Structure

```bash
├── main.py              # FastAPI backend & Inngest functions
├── streamlit_app.py     # Streamlit frontend UI
├── data_loader.py       # PDF processing & embedding logic
├── vector_db.py         # Qdrant connection handler
├── custom_types.py      # Pydantic models
├── pyproject.toml       # Project dependencies (uv)
├── uv.lock              # Lock file for reproducible builds
└── .env                 # API keys and configuration
└── README.md            # Readme File of the project
└──.python-version       # Current Python version
└──.gitignore            # Ignore some file and datas
└──qdrant_storage/       # Vector database infrastructure
```

<br>

## 👩🏻‍💻 Installation & Usage
This project uses  `uv` for dependency management.

* **1.Prerequisite: Install uv:**

If you haven't installed uv yet:
```
# macOS / Linux
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# Windows
powershell -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
```
<br>


* **2.Clone the repository:**
```
git clone https://github.com/mehmetpektass/Agentic-RAG-With-Inngest-LlamaIndex.git
cd Agentic-RAG-With-Inngest-LlamaIndex
```
<br>

* **3. Install Dependencies**

Sync the environment using `uv`. This will automatically create the virtual environment and install all dependencies from `uv.lock.

```
uv sync
```

<br>

* **4. Environment Configuration**

Create a `.env` file in the root directory and add your API keys:
```
# API Keys
GROQ_API_KEY="gsk_..."
COHERE_API_KEY="..."

# Qdrant Config (For Local Docker)
QDRANT_URL="http://localhost:6333"
# QDRANT_API_KEY="" # Leave empty for local
```

<br>

* **5. Start Qdrant (Vector DB)**

Ensure `Docker` is running, then start the `Qdrant` instance:

```
docker run -p 6333:6333 qdrant/qdrant
```

<br>

## ▶️ Running the Application
To run the full stack, you need to open **3 separate terminal windows**. We use `uv` run to execute commands within the virtual environment context.

<br>

**Terminal 1:** Inngest Dev Server Starts the local dashboard to visualize and trigger events.

```
npx inngest-cli@latest dev
```
**Terminal 2:** FastAPI Backend Runs the API server and Inngest client.
```
uv run uvicorn main:app --reload
```

**Terminal 3:** Streamlit Frontend Launches the user interface.

```
uv run streamlit run streamlit_app.py
````

<br>

Access the application at: http://localhost:8501

<br>

## Contribution Guidelines 🚀

##### Pull requests are welcome. If you'd like to contribute, please:
- Fork the repository
- Create a feature branch
- Submit a pull request with a clear description of changes
- Ensure code follows existing style patterns
- Update documentation as needed
