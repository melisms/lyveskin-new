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