# AI Assistant Pro: Tool-Calling AI Agent 🛠️
# 📖 Overview

AI Assistant Pro is a lightweight, intelligent agent built for a 3-day AI Bootcamp Mini-Project, designed to excel in task decomposition and dynamic tool selection.

This project showcases a sophisticated Agentic Controller powered by LangChain and Groq’s Llama3 models, integrated with a suite of tools to handle diverse queries—from real-time web searches to complex math reasoning and document analysis.

With a polished Streamlit UI, robust evaluation framework, and innovative prompt engineering, it achieves:

90% GSM8k benchmark score (math reasoning)

100% LAMA benchmark score (factual recall)

Bootcamp Objectives Achieved ✅

Build a Controller

Integrate Tools

Implement Controller Logic

Benchmark Performance

# 🛠️ Installation
1. Setup Environment
2. python -m venv .venv
3.  .\.venv\Scripts\activate

4. Install dependencies
5. uv pip install -r requirements.txt
6. uv pip freeze > requirements.txt

5. Add API Keys

Create a .env file in the root directory:

GROQ_API_KEY=your_groq_api_key
SERPER_API_KEY=your_serper_api_key

5. Run the Application
streamlit run app.py

# 📂 Project Structure
Agentic_AIi/
│
├── agent/
│   ├── __init__.py
│   ├── controller.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── web_search.py
│   │   ├── calculator.py
│   │   ├── math_solver.py
│   │   └── document_qa.py
│   └── config/
│       ├── __init__.py
│       └── settings.py
│
├── data/
│   ├── documents/          # RAG knowledge base
│   ├── benchmarks/
│   │   ├── lama/
│   │   └── gsm8k/
│   └── results/            # Evaluation results
│
├── evaluation/
│   ├── __init__.py
│   ├── evaluate_lama.py
│   └── evaluate_gsm8k.py
│
├── app.py                  # Streamlit interface
├── requirements.txt
├── config.example.py
└── README.md

# 🎯 Objectives

Agentic Controller: Breaks down complex queries into subtasks.

Tool Integration: Web Search, Calculator, Math Solver, Document QA (RAG).

Controller Logic: Selects or chains tools dynamically.

Benchmarking: Evaluates factual accuracy & reasoning.

# ✨ Features

Robust Prompt Engineering

Distinguishes arithmetic vs. word problems.

Prioritizes RAG for private data.

Supports tool chaining.

Powerful Toolset

🌐 Web Search → Serper API

🧮 Calculator → Sympy + Regex

➗ Math Solver → Llama3-70B via Groq

📄 Document QA → RAG (FAISS, HuggingFace)

Streamlit UI with light/dark themes, chat history, tool cards & Plotly visualizations.

Performance Optimized with caching & error handling.

Evaluation Framework with GSM8k & LAMA benchmarks.

# 🚀 Usage
Launch the App
streamlit run app.py


Access at: http://localhost:8501

Navigate the UI

Chat: Ask queries ("What’s the capital of France?")

Evaluation: Run LAMA & GSM8k tests

Documents: Upload PDF/TXT/DOCX for RAG-based Q&A

About: Explore details

Example Queries

🌐 What’s the latest news in Tokyo?

🧮 Calculate 10+40

➗ A farmer has 15 cows. All but 8 die. How many are left?

📄 What’s in the company handbook? (after uploading a document)

🤖 Who wrote Romeo and Juliet?

# 🔧 Tools
Tool	Purpose	Technology
🌐 Web Search	Real-time info retrieval	Serper API
🧮 Calculator	Arithmetic & math functions	Sympy + Regex
➗ Math Solver	Word problems & reasoning	Llama3-70B via Groq
📄 Document QA	Q&A from local documents (RAG)	FAISS + HuggingFace
📊 Evaluation
Benchmarks

LAMA: Factual recall

GSM8k: Math reasoning

Results

GSM8k Accuracy: 90% (9/10)

LAMA Accuracy: 100% (10/10)

Visualization
graph TD
    A[GSM8k: 90%] --> B[LAMA: 100%]

# 🧠 Agent Decision Process
graph TD
    A[User Query] --> B[Controller Prompt]
    B --> C{Decision}
    C --> |DIRECT| D[LLM Response]
    C --> |TOOL| E[Select Tool]
    C --> |CHAIN| F[Chain Tools]
    E --> G[Execute Tool]
    F --> G
    G --> H[Return Response]

# 🤝 Contributing

Fork the repository

Create a feature branch:

git checkout -b feature/new-tool


Commit changes:

git commit -m "Add new tool"


Push branch & open a Pull Request

✅ Follow PEP 8 & include tests.

# 📜 License

This project is licensed under the MIT License.

# 🏆 Conclusion

AI Assistant Pro is a testament to rapid innovation in just 3 days, delivering a robust, user-friendly, and high-performing AI agent. Built for the AI Bootcamp, it’s ready to impress! 🚀

