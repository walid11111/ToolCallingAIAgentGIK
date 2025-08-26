# type: ignore
import math
import sympy
import re
from langchain.tools import tool
from sympy import pi

@tool
def calculator(expression: str) -> str:
    """Calculator for basic math expressions. Supports arithmetic, sqrt, log, sin, cos, tan."""
    try:
        # Preprocess the expression to handle natural language more robustly
        expr = expression.lower()
        # Remove question marks, periods, etc.
        expr = re.sub(r'[?.,!]', '', expr)
        # Common phrase removals
        expr = re.sub(r'\bwhat is\b|\bcalculate\b|\bfind\b|\bhow much is\b|\bhow many is\b|\bplease\b|\bthe\b|\bcompute\b|\badd\b|\bsubtract\b|\bmultiply\b|\bdivide\b', '', expr).strip()
        # Handle functions
        expr = re.sub(r'\bsquare root\b|\bsqrt\b', 'sqrt', expr)
        expr = re.sub(r'\bcube root\b', '** (1/3)', expr)
        expr = re.sub(r'\bsine\b|\bsin\b', 'sin', expr)
        expr = re.sub(r'\bcosine\b|\bcos\b', 'cos', expr)
        expr = re.sub(r'\btangent\b|\btan\b', 'tan', expr)
        expr = re.sub(r'\blogarithm\b|\blog\b|\blog base 10\b', 'log', expr)
        # Handle operations
        expr = re.sub(r'\badd up\b|\bplus\b', '+', expr)
        expr = re.sub(r'\bminus\b', '-', expr)
        expr = re.sub(r'\btimes\b|\bmultiplied by\b|\bby\b', '*', expr)
        expr = re.sub(r'\bdivided by\b|\bby\b', '/', expr)
        expr = re.sub(r'\bpercent\b|\%', '/100', expr)
        # Handle % off: "20% off of 100" -> "100 * (1 - 20/100)"
        if '% off of' in expr:
            parts = re.split(r'% off of', expr)
            percent = parts[0].strip()
            amount = parts[1].strip()
            expr = f"{amount} * (1 - {percent}/100)"
        # Handle tip: "15% tip on 200" -> "200 * (15/100)"
        if '% tip on' in expr:
            parts = re.split(r'% tip on', expr)
            percent = parts[0].strip()
            amount = parts[1].strip()
            expr = f"{amount} * ({percent}/100)"
        # Handle "and" by removing it, assuming it separates numbers for operation
        expr = re.sub(r'\band\b', '', expr)
        # Special handling for "subtract A from B" -> "B - A"
        if 'from' in expr:
            parts = re.split(r'\bfrom\b', expr)
            if len(parts) == 2:
                subtrahend = parts[0].strip()
                minuend = parts[1].strip()
                expr = f"{minuend} - {subtrahend}"
        # Handle multi-step like "subtract 10 from 50 and then add 5" -> "(50 - 10) + 5"
        if 'and then add' in expr:
            parts = expr.split('and then add')
            expr = f"({parts[0].strip()}) + {parts[1].strip()}"
        if 'and multiply by' in expr:
            parts = expr.split('and multiply by')
            expr = f"({parts[0].strip()}) * {parts[1].strip()}"
        # Remove extra spaces and non-math chars, but keep necessary necessary ones
        expr = re.sub(r'[^0-9+\-*/().\s sqrtlogsincoant]', '', expr).strip()
        # If no operator between numbers, assume multiplication (e.g., "2 3" -> "2*3")
        expr = re.sub(r'(\d+)\s+(\d+)', r'\1*\2', expr)
        # Add parentheses for functions if missing
        if any(func in expr for func in ['sqrt', 'log', 'sin', 'cos', 'tan']):
            expr = re.sub(r'(sqrt|log|sin|cos|tan)\s*(\d+)', r'\1(\2)', expr)
        # Handle degrees for trig functions
        if 'degrees' in expr:
            expr = expr.replace('degrees', '')
            expr = re.sub(r'(sin|cos|tan)\((\d+)\)', r'\1(\2 * pi / 180)', expr)
        # Handle log base 10
        if 'log' in expr and 'base 10' in expr:
            expr = re.sub(r'log\((\d+)\)', r'log(\1, 10)', expr)
        # Handle "add up multiple numbers"
        if '+' not in expr and len(re.findall(r'\d+', expr)) > 2:
            numbers = re.findall(r'\d+', expr)
            expr = '+'.join(numbers)
        # Remove $ signs
        expr = expr.replace('$', '')
        # Evaluate using sympy for safety and flexibility
        result = sympy.sympify(expr).evalf()
        return str(result)
    except Exception as e:
        return f"Calculator Error: {str(e)}"

