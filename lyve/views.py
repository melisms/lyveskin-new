from django.shortcuts import render
from item.models import Category, Item, Ingredient
from django.contrib.auth.models import User
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import difflib
from django.core.cache import cache
from django.views.decorators.cache import cache_page
cache_time = 60 * 10

def home(request):
    return render(request, "lyve/home.html")
@cache_page(cache_time)
def about(request):
    return render(request, "lyve/about.html")
@cache_page(cache_time)
def labeling(request):
    return render(request, "lyve/labeling.html")

@cache_page(cache_time)
def products(request):
    items = Item.objects.all()
    categories = Category.objects.all()
    categorized_items = {category: [] for category in categories}
    for item in items:
        categorized_items[item.category].append(item)

    return render(request, "lyve/products.html",{
        'categories': categories,
        'items': items,
        'categorized_items': categorized_items,
    })

from django.core.paginator import Paginator
@cache_page(cache_time)
def ingredients(request):
    ingredient_list = Ingredient.objects.all()

    # Paginate the ingredient list
    paginator = Paginator(ingredient_list, 100)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "lyve/ingredients.html", {
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),  
        'ingredients': page_obj.object_list,  
    })

@cache_page(cache_time)
def ingredients_view(request, letter=None):
    if letter:
        ingredients = Ingredient.objects.filter(name__istartswith=letter.upper())
    else:
        ingredients = Ingredient.objects.all()

    return render(request, 'lyve/ingredients.html',
            {'ingredients': ingredients, 'letter': letter
            })
@cache_page(cache_time)
def compare(request):
    return render(request, "lyve/compare.html")
@cache_page(cache_time)
def skintype(request):
    return render(request, "lyve/skintype.html")
@cache_page(cache_time)
def skincareroutine(request):
        return render(request, "lyve/skincareroutine.html")
def test(request):
        return render(request, "users/test.html")
    
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.contrib.auth import get_user_model
import json, requests, difflib, logging

User = get_user_model()
SESSION_CHAT_HISTORY_KEY = 'ollama_chat_history'
OLLAMA_API_URL = "http://host.docker.internal:11434/api/generate"

def get_chat_history(session):
    return session.get(SESSION_CHAT_HISTORY_KEY, [])

def add_to_chat_history(session, user_input, model_response):
    history = get_chat_history(session)
    history.append({'user': user_input, 'bot': model_response})
    session[SESSION_CHAT_HISTORY_KEY] = history
    session.modified = True

def serialize_items(items):
    product_data = []
    for item in items:
        image_url = getattr(item.image, 'url', None) if hasattr(item, 'image') else None
        if not image_url:
            image_url = item.image if isinstance(item.image, str) else '/static/images/product-placeholder.jpg'
        product_data.append({
            'id': item.id,
            'name': item.name,
            'image': image_url,
            'url': f"/items/{item.id}/"
        })
    return product_data

def build_prompt(session, question):
    history = get_chat_history(session)
    formatted = "\n".join([f"User: {msg['user']}\nAssistant: {msg['bot']}" for msg in history])
    return f"""
    You are a helpful assistant for a skincare product website.
    Answer the user's question concisely and clearly.
    {formatted}
    User: {question}
    Assistant:
    """

@csrf_exempt
def ask_ollama(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'})

    try:
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'answer': '[JSON Error] Invalid input.'})

        question = body.get('question', '').lower()
        words = question.split()
        cache_key = f"ollama_response:{question}"

        if cached_answer := cache.get(cache_key):
            return JsonResponse({'answer': cached_answer})

        # Match specific item name
        if len(words) >= 2:
            items = cache.get("items_name_list")
            if not items:
                from item.models import Item  # Local import for performance
                items = list(Item.objects.values("id", "name"))
                cache.set("items_name_list", items, 600)

            for item in items:
                item_words = item['name'].lower().split()
                if sum(1 for w in item_words if w in words) >= 3:
                    return JsonResponse({
                        'answer': f"You can visit {item['name']} page.",
                        'redirect': f"/items/{item['id']}/"
                    })

        # Match by category keywords
        category_keywords = {
            "lip care": "Lip Care", "tonic": "Tonic",
            "cleanser": "Cleanser", "moisturizer": "Moisturizer",
            "serum": "Serum", "sunscreen": "Sunscreen",
        }

        for keyword, category_name in category_keywords.items():
            if keyword in question:
                from item.models import Item
                items = Item.objects.filter(category__name__icontains=category_name)[:10]
                if items.exists():
                    return JsonResponse({
                        'answer': f"We have the following {category_name.lower()} products:",
                        'product_results': True,
                        'category': category_name,
                        'products': serialize_items(items)
                    })
                else:
                    answer = f"Sorry, we don't currently have any {category_name.lower()} products listed."
                    cache.set(cache_key, answer, timeout=600)
                    return JsonResponse({'answer': answer})

        # General products response
        if any(w in question for w in ['items', 'products']) and len(words) >= 3:
            from item.models import Item
            items = Item.objects.all()[:10]
            if items.exists():
                return JsonResponse({
                    'answer': "Here are some of our products:",
                    'product_results': True,
                    'category': 'Our Products',
                    'products': serialize_items(items)
                })
            else:
                answer = "Sorry, we don't have any products listed currently."
                cache.set(cache_key, answer, timeout=600)
                return JsonResponse({'answer': answer})

        # User profile (self)
        if "profile" in question and request.user.is_authenticated:
            return JsonResponse({
                "answer": "Redirecting to your profile page.",
                "redirect": f"/profile/{request.user.id}/"
            })

        # User profile (others)
        if "profile" in words:
            possible_names = [w for w in words if w != "profile"]
            if possible_names:
                usernames = cache.get("all_usernames")
                if not usernames:
                    usernames = list(User.objects.values_list('username', flat=True))
                    cache.set("all_usernames", usernames, 600)

                for name in possible_names:
                    matches = difflib.get_close_matches(name, [u.lower() for u in usernames], n=1, cutoff=0.7)
                    if matches:
                        matched_user = User.objects.get(username__iexact=matches[0])
                        return JsonResponse({
                            "answer": f"Redirecting to {matched_user.username}'s profile page.",
                            "redirect": f"/profile/{matched_user.id}/"
                        })

        # Default: Ask Ollama
        prompt = build_prompt(request.session, question)
        try:
            response = requests.post(
                OLLAMA_API_URL,
                json={"model": "mistral", "prompt": prompt, "stream": False},
                
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"RequestException occurred: {e}")
            return JsonResponse({'answer': '[Request Error] Failed to connect to language model.'})

        answer = response.json().get('response', 'No answer found.')
        add_to_chat_history(request.session, question, answer)
        cache.set(cache_key, answer, timeout=600)
        return JsonResponse({'answer': answer})

    except Exception as e:
        logging.getLogger(__name__).error("Unexpected error in ask_ollama", exc_info=True)
        return JsonResponse({'answer': 'An internal error has occurred.'})

