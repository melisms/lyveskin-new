from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.cache import cache

SESSION_CHAT_HISTORY_KEY = 'ollama_chat_history'

def clear_ollama_cache_and_history(sender, request, user, **kwargs):
    # Clear session chat history
    request.session.pop(SESSION_CHAT_HISTORY_KEY, None)
    request.session.modified = True

    # Clear all cached Ollama keys tracked
    keys = cache.get('ollama_cached_questions', set())
    for key in keys:
        cache.delete(key)
    cache.delete('ollama_cached_questions')

user_logged_in.connect(clear_ollama_cache_and_history)
user_logged_out.connect(clear_ollama_cache_and_history)
