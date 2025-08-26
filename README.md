AI Assistant Pro: Tool-Calling AI Agent 🛠️

# 📖 Overview
AI Assistant Pro is a lightweight, intelligent agent built for a 3-day AI Bootcamp Mini-Project, designed to excel in task decomposition and dynamic tool selection. This project showcases a sophisticated Agentic Controller powered by LangChain and Groq’s Llama3 models, integrated with a suite of tools to handle diverse queries—from real-time web searches to complex math reasoning and document analysis. With a polished Streamlit UI, robust evaluation framework, and innovative prompt engineering, it achieves impressive benchmark results (80% GSM8k, 90% LAMA) while meeting all bootcamp objectives: building a controller, integrating tools, implementing logic, and benchmarking performance.


# 🛠️ Installation
Follow these steps to set up the project locally:

Set Environment Variables:Create a .env file in the project root:
python -m venv .venv
.\.venv\Scripts\Activate

uv pip install -r requirements.txt
uv pip freeze > requirements.txt 

Run the Application:Start the Streamlit app:
streamlit run app.py

Add the following API keys (obtain from Groq and Serper):
GROQ_API_KEY=your_groq_api_key
SERPER_API_KEY=your_serper_api_key


# Complete project Structure:
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
│   ├── documents/          # For RAG knowledge base
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
├── app.py                  # Gradio interface
├── requirements.txt
├── config.example.py       # Example config file
└── README.



# 🎯 Objectives
Agentic Controller: Decomposes complex user queries into subtasks using a finely tuned prompt.
Tool Integration: Connects four tools: Web Search, Calculator, Math Solver, and Document QA (RAG).
Controller Logic: Dynamically selects tools or chains them for multi-step tasks.
Benchmarking: Evaluates factual accuracy (LAMA) and reasoning (GSM8k) with high performance.


# ✨ Features

Robust Prompt Engineering: A sophisticated controller prompt distinguishes between simple arithmetic (Calculator) and complex word problems (Math Solver), prioritizes Document QA for private data, and supports tool chaining.
Powerful Toolset:
🌐 Web Search: Fetches real-time data via Serper API.
🧮 Calculator: Handles arithmetic and functions (e.g., sqrt, sin) using Sympy.
➗ Math Solver: Solves GSM8k-style word problems with step-by-step reasoning via Llama3-70b.
📄 Document QA: Retrieves answers from local PDF/TXT/DOCX files using RAG (FAISS, HuggingFace).


Themed Streamlit UI: Interactive interface with light/dark themes, chat history, tool status cards, and Plotly visualizations.
Performance Optimization: Uses lru_cache for tool call efficiency and robust error handling.
Evaluation Framework: Benchmarks factual accuracy (LAMA) and reasoning (GSM8k) with clear reporting.




# 🚀 Usage

Launch the App:Run streamlit run app.py and access the UI at http://localhost:8501.

Navigate the UI:

Chat: Ask queries (e.g., “What’s the capital of France?”, “Solve: A car travels 60 mph for 3 hours”).
Evaluation: Run LAMA and GSM8k benchmarks to view performance.
Documents: Upload PDF/TXT/DOCX files for RAG-based Q&A.
About: Explore project details and features.


Example Queries:

🌐 “What’s the latest news in Tokyo?”
🧮 “Calculate 10+40”
➗ “A farmer has 15 cows. All but 8 die. How many are left?”
📄 “What’s in the company handbook?” (after uploading a document)
🤖 “Who wrote Romeo and Juliet?”



# 🔧 Tools

Tool
Purpose
Technology

Web Search
Real-time information retrieval
Serper API

Calculator
Simple arithmetic and math functions
Sympy with regex preprocessing

Math Solver
Complex word problems with reasoning
Llama3-70b via Groq

Document QA
Answers from local documents
RAG (FAISS, HuggingFace)


# 📊 Evaluation
The project includes scripts to evaluate performance on two benchmarks:

LAMA: Tests factual recall (e.g., “The capital of France is [MASK].”).
GSM8k: Tests mathematical reasoning (e.g., “A car travels 60 mph for 2.5 hours...”).

Running Benchmarks
In the Streamlit UI, navigate to the Evaluation page and click “Run LAMA” or “Run GSM8K”. Results are displayed with accuracy and detailed logs.
Sample Results

GSM8k Accuracy: 90% (9/10 correct answers).
LAMA Accuracy: 100% (10/10 correct answers).

Benchmark Visualization
graph TD
    A[GSM8k: 90%] --> B[LAMA: 100%]

🧠 Agent Decision Process
graph TD
    A[User Query] --> B[Controller Prompt]
    B --> C{Decision}
    C --> |DIRECT| D[LLM Response]
    C --> |TOOL| E[Select Tool]
    C --> |CHAIN| F[Chain Tools]
    E --> G[Execute Tool]
    F --> G
    G --> H[Return Response]


    # Project Flow Diagram
text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │    │   Streamlit       │    │   Controller    │
│   (Input)       │───▶│   Interface     │───▶│   Agent         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼ Decision Making
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Evaluation    │    │   Tool          │    │   Response      │
│   Results       │◀──│   Selection     │◀──│   Generation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
       │                       │
       │                       ├─▶ 🌐 Web Search (Serper API)
       │                       ├─▶ 🧮 Calculator
       │                       ├─▶ ➗ Math Solver (Llama3-70B)
       │                       ├─▶ 📄 Document QA (RAG)
       │                       └─▶ 🤖 Direct Answer (Llama3-8B)
       │
       └───────▶ Benchmark Comparison
                 (LAMA & GSM8k)


🏗️ System Architecture
graph TD
    A[User Query] --> B[Streamlit UI]
    B --> C[Controller Agent]
    C --> D{Tools}
    D --> E[Web Search]
    D --> F[Calculator]
    D --> G[Math Solver]
    D --> H[Document QA]
    C --> I[LLM]
    D --> I
    I --> J[Response]
    J --> B

# 🤝 Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a feature branch (git checkout -b feature/new-tool).
Commit changes (git commit -m 'Add new tool').
Push to the branch (git push origin feature/new-tool).
Open a Pull Request.

Please ensure code follows PEP 8 and includes tests.
📜 License
This project is licensed under the MIT License. See the LICENSE file for details.

AI Assistant Pro is a testament to rapid innovation in a 3-day sprint, delivering a robust, user-friendly, and high-performing AI agent. Built for the AI Bootcamp, it’s ready to impress! 🏆# Tool_Calling_AI_Agent
