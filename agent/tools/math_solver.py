# type: ignore
import os
from langchain.tools import tool
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@tool
def math_solver(problem: str) -> str:
    """Solves complex math word problems using step-by-step reasoning. Specialized for GSM8k-style problems."""
    try:
        if not GROQ_API_KEY:
            return "Math Solver Error: API key not set."
        math_llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model="llama3-70b-8192",
            temperature=0,
            max_tokens=1024,
        )
        prompt = f"""Solve the following math problem step by step. Show your reasoning and provide the final answer. Problem: {problem}
        Format the final answer as: \\boxed{{answer}}"""
        response = math_llm.invoke(prompt)
        return f"➗ Math Solution (via Llama3-70B):\n\n{response.content}"
    except Exception as e:
        return f"Math Solver Error: {str(e)}"
