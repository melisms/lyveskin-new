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

@cache_page(cache_time)
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
    
from django.contrib.auth import get_user_model
User = get_user_model()
@csrf_exempt
def ask_ollama(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            question = body.get('question', '').lower()
            words = question.split()
            
            cache_key = f"ollama_response:{question}"
            cached_answer = cache.get(cache_key)
            if cached_answer:
                return JsonResponse({'answer': cached_answer})
            
            if len(words) >= 2:
                items = Item.objects.all()
                matched_items = []

                for item in items:
                    item_name_words = item.name.lower().split()
                    matched_word_count = sum(1 for w in item_name_words if w in words)

                    if matched_word_count >= 2:
                        matched_items.append(item)

                if matched_items:
                    matched_item = matched_items[0]  
                    return JsonResponse({
                        'answer': f"You can visit {matched_item.name} page.",
                        'redirect': f"/items/{matched_item.id}/"
                    })
            
            # routes = {
            #     "home": "/",
            #     "compare": "/items/compare/",
            #     "ingredients": "/ingredient/",
            #     "ingredient": "/ingredient/",
            #     "forum": "/forum/",
            #     "skin type": "/skintype/",
            #     "skintype": "/skintype/",
            #     "skincare routine": "/skincareroutine/",
            #     "labeling system": "/labeling/",
            #     "labeling": "/labeling/",
            #     "routine": "/skincareroutine/",
            #     "items": "/items/browse/",
            #     "item": "/items/browse/",
            #     "add product": "/items/new/",
            #     "add": "/items/new/",
            #     "products": "/items/browse/",
            #     "product": "/items/browse/",
            # }
            
            category_keywords = {
                "lip care": "Lip Care",
                "tonic": "Tonic",
                "cleanser": "Cleanser",
                "moisturizer": "Moisturizer",
                "serum": "Serum",
                "sunscreen": "Sunscreen",
            }
            
            # for keyword, route in routes.items():
            #     if keyword in question:
            #         return JsonResponse({
            #             'answer': f"You can visit {keyword.title()} page.",
            #             'redirect': route
            #         })
                    
            for keyword, category_name in category_keywords.items():
                if keyword in question:
                    items = Item.objects.filter(category__name__icontains=category_name)
                    if items.exists():
                        item_names = [item.name for item in items[:10]] 
                        answer = f"We have the following {category_name.lower()} products: " + ", ".join(item_names) + "."
                    else:
                        answer = f"Sorry, we don't currently have any {category_name.lower()} products listed."
                    cache.set(cache_key, answer, timeout=600)
                    return JsonResponse({'answer': answer})
            
            if any(word in question for word in ['items', 'products']) and len(words) >= 3:
                general_items = Item.objects.all()
                if general_items.exists():
                    item_names = [item.name for item in general_items[:10]]
                    answer = "Here are some of our products: " + ", ".join(item_names) + "."
                else:
                    answer = "Sorry, we don't have any products listed currently."
                cache.set(cache_key, answer, timeout=600)
                return JsonResponse({'answer': answer})    
                    
            if "profile" in question and request.user.is_authenticated:
                return JsonResponse({
                    "answer": "Redirecting to your profile page.",
                    "redirect": f"/profile/{request.user.id}/"
                })
            if "profile" in words:
                possible_names = [w for w in words if w != "profile"]

                if possible_names:
                    users = User.objects.all()
                    usernames = [user.username.lower() for user in users]

                    for name in possible_names:
                        matches = difflib.get_close_matches(name, usernames, n=1, cutoff=0.7)
                        if matches:
                            matched_username = matches[0]
                            user = User.objects.get(username__iexact=matched_username)
                            return JsonResponse({
                                "answer": f"Redirecting to {user.username}'s profile page.",
                                "redirect": f"/profile/{user.id}/"
                            })            
            prompt = f"""
            You are a helpful assistant for a skincare product website.
            Answer the user's question concisely and clearly.

            Question: {question}
            Answer:
            """
            ollama_response = requests.post(
                "http://host.docker.internal:11434/api/generate",
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=10
            )
            ollama_response.raise_for_status() 
            response_json = ollama_response.json()
            answer = response_json.get('response', 'No answer found.')
            cache.set(cache_key, answer, timeout=600)

            return JsonResponse({'answer': answer})
        except requests.exceptions.RequestException as e:
            print(f"RequestException occurred: {e}")
            return JsonResponse({'answer': '[Request Error] An error occurred while processing your request.'})
        except ValueError as e:
            print(f"ValueError occurred: {e}")
            return JsonResponse({'answer': '[JSONDecodeError] Invalid JSON response received.'})
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error("An unexpected error occurred in ask_ollama", exc_info=True)
            return JsonResponse({'answer': 'An internal error has occurred.'})
    else:
        return JsonResponse({'error': 'POST method required'})
