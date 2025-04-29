import requests

def ollama_soru_sor(soru):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "mistral",
        "prompt": soru,
        "stream": False
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # HTTP hatası varsa çıkar
        response_json = response.json()  # JSON hatası varsa try yakalar
        return response_json.get("response", "Cevap bulunamadı.")
    except requests.exceptions.RequestException as e:
        return f"[İSTEK HATASI] {str(e)}"
    except ValueError:
        return "[JSONDecodeError] Geçersiz JSON cevabı alındı."
    except Exception as e:
        return f"[GENEL HATA] {str(e)}"

# 🔁 Sonsuz döngü
while True:
    soru = input("Modele sorulacak cümleyi yazın (çıkmak için 'çık' yazın): ")
    if soru.lower() == "çık":
        print("Görüşmek üzere! 👋")
        break
    cevap = ollama_soru_sor(soru)
    print("Modelin Cevabı:", cevap)
