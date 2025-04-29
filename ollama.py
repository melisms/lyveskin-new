import requests

def ask_ollama(question):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "mistral",
        "prompt": question,
        "stream": False
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise an error for HTTP errors
        response_json = response.json()  # Catch JSON errors
        return response_json.get("response", "No answer found.")
    except requests.exceptions.RequestException as e:
        return f"[REQUEST ERROR] {str(e)}"
    except ValueError:
        return "[JSONDecodeError] Invalid JSON response received."
    except Exception as e:
        return f"[GENERAL ERROR] {str(e)}"

# 🔁 Infinite loop
while True:
    question = input("Enter a prompt for the model (type 'exit' to quit): ")
    if question.lower() == "exit":
        print("Goodbye! 👋")
        break
    answer = ask_ollama(question)
    print("Model's Answer:", answer)
