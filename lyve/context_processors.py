def chat_history(request):
    return {
        'chat_history': request.session.get('ollama_chat_history', [])
    }
