# type: ignore
import sys
import os
import functools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.agents import Tool
from agent.tools.web_search import web_search
from agent.tools.calculator import calculator
from agent.tools.math_solver import math_solver
from agent.tools.document_qa import document_qa
from agent.config.settings import GROQ_API_KEY


# LLM
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama3-8b-8192",  # As confirmed
    temperature=0,
    max_tokens=1024,
)

# Tools
tools = [
    Tool(
        name="Web Search",
        func=web_search,
        description="For up-to-date information, current events, or facts that may change over time."
    ),
    Tool(
        name="Calculator",
        func=calculator,
        description="For simple mathematical calculations and arithmetic problems."
    ),
    Tool(
        name="Math Solver",
        func=math_solver,
        description="For complex math word problems requiring step-by-step reasoning."
    ),
    Tool(
        name="Document QA",
        func=document_qa,
        description="For answering questions based on local documents and knowledge base."
    )
]

# Enhanced controller prompt (improved for better distinction between Calculator and Math Solver)
# Enhanced controller prompt (improved for better distinction between Calculator and Math Solver)
controller_prompt = PromptTemplate(
    input_variables=["query"],
    template=(
        "You are an advanced controller AI tasked with analyzing user queries and selecting the most appropriate tool or combination of tools to provide accurate and efficient answers. "
        "Your goal is to understand the query's intent, context, and requirements, then decide the best approach. "
        "Follow the guidelines below and provide a clear reasoning for your choice.\n\n"
        "Available Tools:\n"
        "- WEB_SEARCH: For recent information (post-2023), current events, news, or facts that may change (e.g., weather, stock prices).\n"
        "- CALCULATOR: For simple arithmetic operations or direct math expressions without story context (e.g., '2+2', 'sqrt(16)', '15% of 80', 'sin(30)'). Use only if it's a straightforward calculation.\n"
        "- MATH_SOLVER: For complex math word problems with story context, scenarios, units, or requiring logical reasoning/multi-step solutions (e.g., 'A car travels 60 mph for 2 hours, how far?', 'If John has 5 apples and gives away 2, how many left?'). If there's a narrative, objects, or conditions, prefer this over CALCULATOR.\n"
        "- DOCUMENT_QA: For questions about content in local files (PDF, TXT, DOCX) in the knowledge base, especially when the query pertains to any private documents, proprietary data, personal profiles, university prospectuses, or any other user-uploaded personal or confidential content. Prioritize this tool for all queries that reference or imply access to uploaded, private, or user-specific information not publicly available.\n"
        "- DIRECT: For general knowledge questions (pre-2023) or simple queries not requiring tools.\n\n"
        "Guidelines for Tool Selection:\n"
        "1. Analyze the query for keywords, context, and intent:\n"
        "   - Current events, news, or time-sensitive data (e.g., 'latest news', 'weather today') → WEB_SEARCH.\n"
        "   - Direct numeric calculations or math expressions without narrative (e.g., '5 * 3', 'sin(30)', '25 minus 7') → CALCULATOR.\n"
        "   - Word problems with story, scenarios, units, or reasoning (e.g., 'A bike goes 20 km/h for 3.5 hours', 'Sarah is three times older than her brother') → MATH_SOLVER. If it involves objects, people, or multi-step logic, use MATH_SOLVER even if simple arithmetic is involved.\n"
        "   - Questions about specific documents or policies (e.g., 'What’s in the company handbook?'), or any private/personal data (e.g., 'When was the company founded?', 'What is in my profile?', 'Details from the prospectus') → DOCUMENT_QA. Give strong preference to DOCUMENT_QA for all queries that mention or imply private, personal, uploaded, or confidential content, even if public data might exist elsewhere; assume such queries refer to user-provided documents.\n"
        "   - General knowledge or simple facts (e.g., 'Capital of France') → DIRECT.\n"
        "2. For hybrid queries (e.g., 'Search for today’s temperature and calculate its Fahrenheit equivalent'):\n"
        "   - Select CHAIN and specify the order of tools (e.g., 'WEB_SEARCH → CALCULATOR').\n"
        "3. If unsure, prioritize DOCUMENT_QA for internal data (e.g., uploaded PDFs, texts), WEB_SEARCH for external data, or CHAIN for multi-step tasks.\n"
        "4. Avoid using tools unnecessarily; DIRECT is preferred for simple, known facts.\n"
        "5. Distinguish carefully: If query has a story like 'a bakery has cookies' or 'a tank holds liters', it's MATH_SOLVER. If it's just '20 * 3.5', it's CALCULATOR.\n"
        "6. If no tool fits or the query is ambiguous, ask for clarification via DIRECT with a prompt like: 'Can you clarify what you mean by [query]?'\n\n"
        "Query Analysis Steps:\n"
        "1. Identify the main topic (e.g., math, news, document content).\n"
        "2. Check for time sensitivity or external data needs.\n"
        "3. Determine if reasoning or computation is required: Story/context → MATH_SOLVER, direct expr → CALCULATOR.\n"
        "4. Evaluate if local documents are relevant, especially if the query relates to any private, personal, uploaded, or confidential content (e.g., profiles, prospectuses, company details) and strongly favor DOCUMENT_QA in such cases.\n"
        "5. Decide if multiple tools are needed for a complete answer.\n\n"
        "User query: {query}\n\n"
        "Output Format:\n"
        "Decision: [WEB_SEARCH | CALCULATOR | MATH_SOLVER | DOCUMENT_QA | DIRECT | CHAIN]\n"
        "Tool Order (if CHAIN): [List tools in order, e.g., 'WEB_SEARCH → CALCULATOR']\n"
        "Reasoning: [One-sentence explanation of why this tool/combination was chosen]"
    ),
)

# Initialize agent with create_react_agent (updated with required variables)
agent_prompt = PromptTemplate(
    input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
    template=(
        "You are a helpful AI assistant with access to the following tools: {tools}\n\n"
        "Tool names: {tool_names}\n\n"
        "Answer the following question as best you can, using the provided tools if necessary. "
        "Think step by step, and chain tools if needed for complex queries. "
        "For each step, explain your reasoning and use the format: [Action: Tool Name] or [Action: Direct Answer].\n\n"
        "Question: {input}\n\n"
        "Agent Scratchpad: {agent_scratchpad}"
    )
)

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=agent_prompt
)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True
)

# Cache for performance
@functools.lru_cache(maxsize=100)
def cached_tool_call(tool_name, query):
    if tool_name == "Web Search":
        return web_search(query)
    elif tool_name == "Calculator":
        return calculator(query)
    elif tool_name == "Math Solver":
        return math_solver(query)
    elif tool_name == "Document QA":
        return document_qa(query)
    return None

def ask_agent(query: str):
    try:
        decision_prompt = controller_prompt.format(query=query)
        decision_resp = llm.invoke(decision_prompt)
        decision_text = decision_resp.content if hasattr(decision_resp, 'content') else str(decision_resp)
        print(f"Controller Decision: {decision_text}")

        # Parse decision and tool order
        decision_lines = decision_text.strip().split("\n")
        decision = ""
        tool_order = ""
        for line in decision_lines:
            if line.startswith("Decision:"):
                decision = line.replace("Decision:", "").strip()
            elif line.startswith("Tool Order:"):
                tool_order = line.replace("Tool Order:", "").strip()

        if decision == "CHAIN":
            result = agent_executor.invoke({"input": query})["output"]
            return (result, f"🔗 Chained Tools: {tool_order}")
        elif decision == "WEB_SEARCH":
            result = cached_tool_call("Web Search", query)
            return (result, "🌐 Web Search Tool")
        elif decision == "CALCULATOR":
            result = cached_tool_call("Calculator", query)
            return (result, "🧮 Calculator Tool")
        elif decision == "MATH_SOLVER":
            result = cached_tool_call("Math Solver", query)
            return (result, "➗ Math Solver Tool")
        elif decision == "DOCUMENT_QA":
            result = cached_tool_call("Document QA", query)
            return (result, "📄 Document QA Tool")
        else:  # DIRECT or unclear
            answer = llm.invoke(query)
            return (answer.content, "🤖 Direct Answer (llama3-8b-8192)")
    except Exception as e:
        return (f"Error: {str(e)}", "❌ Error")