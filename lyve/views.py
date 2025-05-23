from django.shortcuts import render
from item.models import Category, Item, Ingredient

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging

def home(request):
    return render(request, "lyve/home.html")

def about(request):
    return render(request, "lyve/about.html")

def labeling(request):
    return render(request, "lyve/labeling.html")
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


def ingredients(request):
    ingredient_list = Ingredient.objects.all()

    # Paginate the ingredient list
    paginator = Paginator(ingredient_list, 100)  # Show 5 ingredients per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "lyve/ingredients.html", {
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),  # Pass if the list is paginated
        'ingredients': page_obj.object_list,  # Pass the ingredients for the current page
    })


def ingredients_view(request, letter=None):
    if letter:
        ingredients = Ingredient.objects.filter(name__istartswith=letter.upper())
    else:
        ingredients = Ingredient.objects.all()

    return render(request, 'lyve/ingredients.html',
            {'ingredients': ingredients, 'letter': letter
             })


def compare(request):
    return render(request, "lyve/compare.html")

def skintype(request):
    return render(request, "lyve/skintype.html")

def skincareroutine(request):
        return render(request, "lyve/skincareroutine.html")

@csrf_exempt
def ask_ollama(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            question = body.get('question', '')

            ollama_response = requests.post(
                "http://host.docker.internal:11434/api/generate",
                json={
                    "model": "mistral",
                    "prompt": question,
                    "stream": False
                }
            )
            ollama_response.raise_for_status()  # Raise an error for HTTP errors
            response_json = ollama_response.json()
            answer = response_json.get('response', 'No answer found.')

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
