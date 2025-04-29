import requests

def ollama_soru_sor(soru):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "mistral",
        "prompt": soru,
        "stream": False  # ❗ Burayı düzeltiyoruz
    }
    response = requests.post(url, json=data)
    return response.json()["response"]

# 🔥 Sonsuz döngü başlıyor
while True:
    soru = input("Modele sorulacak cümleyi yazın (çıkmak için 'çık' yazın): ")
    if soru.lower() == "çık":
        print("Görüşmek üzere! 👋")
        break
    cevap = ollama_soru_sor(soru)
    print("Modelin Cevabı:", cevap)
