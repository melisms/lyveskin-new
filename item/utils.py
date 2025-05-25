def get_me_queryset(category):
    valid_categories = {
        'sunscreen': 'Sunscreen',
        'moisturizer': 'Moisturizer',
        'cleanser': 'Cleanser',
        'serum': 'Serum',
        'mask': 'Mask',
    }

    category_name = valid_categories.get(category.lower())
    from .models import Item
    if category_name:
        return Item.objects.filter(category__name=category_name)
    return Item.objects.none()

import requests
def detect_safety(name):
    prompt = (
        f"Classify the safety of this ingredient as 'S' (Safe), 'R' (Risky), or 'N' (Neutral). "
        f"Also provide a brief note explaining the decision. "
        f"Format your response exactly like this:\n"
        f"Safety: <S|R|N>\nNote: <explanation>\n"
        f"Ingredient: {name}"
    )

    try:
        response = requests.post(
            "http://host.docker.internal:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False,
            }
        )
        response.raise_for_status()
        result = response.json()
        text = result.get('response', '').strip().upper()
        lines = text.splitlines()
        safety = None
        note = ""

        for line in lines:
            if line.upper().startswith("SAFETY:"):
                safety = line.split(":", 1)[1].strip().upper()
            elif line.upper().startswith("NOTE:"):
                note = line.split(":", 1)[1].strip()

        if safety in ['S', 'R', 'N']:
            return safety, note
    except Exception as e:
        print(f"AI call failed: {e}")
    return 'N', 'Could not determine safety, defaulting to Neutral.'

from django.test import RequestFactory
from django.utils.cache import get_cache_key
from django.core.cache import cache
from django.urls import reverse
def clear_cache_for_detail(request, pk):
    rf = RequestFactory()
    path = reverse('item:detail', kwargs={'pk': pk})
    fake_request = rf.get(path)
    fake_request.user = request.user 
    key = get_cache_key(fake_request)
    if key:
        cache.delete(key)

def clear_cache_for_browse(request):
    rf = RequestFactory()
    path = reverse('item:browse')
    fake_request = rf.get(path)
    fake_request.user = request.user
    key = get_cache_key(fake_request)
    if key:
        cache.delete(key)

def clear_cache_for_comparison(request, item_id1, item_id2):
    rf = RequestFactory()
    path = reverse('item:comparison_page', kwargs={'item_id1': item_id1, 'item_id2': item_id2})
    fake_request = rf.get(path)
    fake_request.user = getattr(request, 'user', None)
    key = get_cache_key(fake_request, method='GET')
    if key:
        cache.delete(key)
        return True
    return False
