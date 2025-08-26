# type: ignore
from agent.controller import ask_agent

def evaluate_lama():
    lama_data = {
        "1": {"question": "The capital of France is [MASK].", "answer": ["Paris"]},
        "2": {"question": "The largest planet in our solar system is [MASK].", "answer": ["Jupiter"]},
        "3": {"question": "The chemical symbol for gold is [MASK].", "answer": ["Au"]},
        "4": {"question": "The author of 'Romeo and Juliet' is [MASK].", "answer": ["William Shakespeare", "Shakespeare"]},
        "5": {"question": "The longest river in the world is [MASK].", "answer": ["Nile", "Amazon"]},
        "6": {"question": "The largest ocean on Earth is the [MASK] Ocean.", "answer": ["Pacific"]},
        "7": {"question": "The process by which plants make food is called [MASK].", "answer": ["photosynthesis"]},
        "8": {"question": "The hardest natural substance on Earth is [MASK].", "answer": ["diamond"]},
        "9": {"question": "The country with the largest population in the world is [MASK].", "answer": ["China", "India"]},
        "10": {"question": "The smallest bone in the human body is located in the [MASK].", "answer": ["ear"]}
    }
    correct = 0
    results = ""
    for key, item in lama_data.items():
        query = item["question"].replace("[MASK]", "what?")
        response, _ = ask_agent(query)
        if any(ans.lower() in response.lower() for ans in item["answer"]):
            correct += 1
        results += f"Q: {item['question']}\nA: {response}\nCorrect: {item['answer']}\n\n"
    accuracy = (correct / len(lama_data)) * 100
    return f"LAMA Accuracy: {accuracy}%\n\n{results}"