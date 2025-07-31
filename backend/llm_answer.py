import requests

def generate_llm_answer(results, query, n=5):
    context = "\n\n".join([
        f"Title: {r['title']}\nBody: {r['body_text']}" for r in results[:n]
    ])
    prompt = f"""Given the following search results, answer the user's query: "{query}"

Search Results:
{context}

Answer:"""
    response = requests.post(
        "http://localhost:11434/api/generate",  # Use host.docker.internal if needed
        json={
            "model": "llama2",  # Change to your pulled model name
            "prompt": prompt,
            "stream": False
        }
    )
    data = response.json()
    return data.get("response", "").strip()