# Calculator Qestion:

what is 3+5
Compute 8 + 11 + 13 + 5
subtract 10-5


# Math Solver Test Cases

Question: "A store has 20 apples. If 5 are sold and then 10 more are added, how many apples are there?"

Expected Tool: Math Solver
Expected Answer: Contains "\boxed{25}" (or clearly states 25 apples after reasoning)


Question: "If a car travels at 50 mph for 4 hours, how far does it go?"

Expected Tool: Math Solver
Expected Answer: Contains "\boxed{200}" (or clearly states 200 miles)


Question: "A recipe needs 2/3 cup of sugar. If you make 1/2 the recipe, how much sugar do you need?"

Expected Tool: Math Solver
Expected Answer: Contains "\boxed{\frac{1}{3}}" or "0.333333333333333" (or equivalent)



# Web Search Test Cases
These require recent or time-sensitive data, triggering the Serper API.

Question: "What’s the weather in London today?"

Question: "Who won the latest Super Bowl?"



# Document QA Test Cases

Ducoments question:
Name two core values of TechNova Solutions.
How many clients does TechNova Solutions serve worldwide?
What is the contact email for TechNova Solutions




# LLM Decide:
These are general knowledge questions that don’t require tools.

Question: "What is the capital of Japan?"

Expected Tool: Direct
Expected Answer: "Tokyo"


Question: "Who wrote 'Pride and Prejudice'?"

Expected Tool: Direct
Expected Answer: "Jane Austen"


Question: "What is the chemical symbol for oxygen?"

Expected Tool: Direct
Expected Answer: "O"
