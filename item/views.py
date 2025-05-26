from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Item, Category, Ingredient
from .forms import NewItemForm
from django.db.models import Q
from collections import Counter
from .forms import ComparisonForm,NewItemForm
from django.contrib import messages
from .utils import detect_safety, clear_cache_for_detail, clear_cache_for_browse, clear_cache_for_comparison
from django.views.decorators.cache import cache_page
from django.core.cache import cache

def detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    ingredients = item.ingredients.all()
    
    cache_key = f'health_score_item_{pk}'
    health_data = cache.get(cache_key)
    
    if not health_data:
        health_data = item.calculate_health_score()
        cache.set(cache_key, health_data, 600)
    
    return render(request, 'item/detail.html', {
        'item': item,
        'ingredients': ingredients,
        'health_score': health_data['score'],
        'safe_count': health_data['safe'],
        'risky_count': health_data['risky'],
    })
@login_required
def add_to_favorites(request, pk):
    item = get_object_or_404(Item, pk=pk)
    profile = request.user.userprofile

    if item in profile.favorites.all():
        messages.info(request, 'This item is already in your routine.')
    else:
        profile.favorites.add(item)
        messages.success(request, 'Item added to your routine!')

    return redirect('item:detail', pk=pk)
@login_required
def remove_from_favorites(request, pk):
    item = get_object_or_404(Item, pk=pk)
    profile = request.user.userprofile

    if item in profile.favorites.all():
        profile.favorites.remove(item)
        messages.success(request, 'Item removed from your routine!')
    else:
        messages.info(request, 'This item is not in your routine.')

    return redirect('item:detail', pk=pk)

def create_item(request):
    if request.method == 'POST':
        form = NewItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save()
            for ingredient in item.ingredients.all():
                safety, note = detect_safety(ingredient.name)
                if ingredient.safety != safety or ingredient.note != note:
                    ingredient.safety = safety
                    ingredient.note = note
                    ingredient.save()
            clear_cache_for_detail(request, item.pk)
            clear_cache_for_browse()
            messages.success(request, 'Item added successfully.')
            return redirect('item:detail', pk=item.pk)
    else:
        form = NewItemForm()
    return render(request, 'item/form.html', {'form': form, 'title': 'Create New Item'})

def browse(request):
    query = request.GET.get('query','')
    category_id = request.GET.get('category', 0)
    cache_key = f'browse_cache::query={query}&category={category_id}'
    cached_response = cache.get(cache_key)
    if cached_response:
        return cached_response
    categories = Category.objects.all()
    items = Item.objects.filter()
    if category_id:
        items = items.filter(category=category_id)
    if query:
        items = items.filter(Q(name__icontains=query)|Q(brands__icontains=query))
    response = render(request, 'item/browse.html', {
        'items': items,
        'query': query,
        'categories': categories,
        'category_id': int(category_id),
    })
    cache.set(cache_key, response, 300)
    return response

def compare_items(request):
    if request.method == 'POST':
        form = ComparisonForm(request.POST)

        if form.is_valid():
            category = form.cleaned_data['category']
            item1 = form.cleaned_data['item1']
            item2 = form.cleaned_data['item2']
            clear_cache_for_comparison(request, item1.id, item2.id)
            # Get the ingredients for each item and count the safety levels
            item1_ingredients = item1.ingredients.all()
            item2_ingredients = item2.ingredients.all()
            item1_counts = Counter(ingredient.safety for ingredient in item1_ingredients)
            item2_counts = Counter(ingredient.safety for ingredient in item2_ingredients)

            return render(request, 'item/comparison_page.html', {
                'category': category,
                'item1': item1,
                'item2': item2,
                'item1_safe_count': item1_counts['S'],
                'item1_risky_count': item1_counts['R'],
                'item2_safe_count': item2_counts['S'],
                'item2_risky_count': item2_counts['R'],})
    else:
        form = ComparisonForm()
    return render(request, 'item/compare_items.html', {'form': form})
@cache_page(60 * 5)
def comparison_page(request, item_id1, item_id2):
    # Retrieve the items from the database
    item1 = get_object_or_404(Item, pk=item_id1)
    item2 = get_object_or_404(Item, pk=item_id2)

    # Count the number of risky and safe ingredients for each item
    item1_ingredients = item1.ingredient_set.values_list('safety', flat=True)
    item2_ingredients = item2.ingredient_set.values_list('safety', flat=True)
    item1_risky_count = item1_ingredients.count('R')
    item2_risky_count = item2_ingredients.count('R')
    item1_safe_count = item1_ingredients.count('S')
    item2_safe_count = item2_ingredients.count('S')

    return render(request, 'item/comparison_page.html', {
        'item1': item1,
        'item2': item2,
        'item1_safe_count': item1_safe_count,
        'item1_risky_count': item1_risky_count,
        'item2_safe_count': item2_safe_count,
        'item2_risky_count': item2_risky_count,
    })
@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    if request.method == 'POST':
        form = NewItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            for ingredient in item.ingredients.all():
                safety, note = detect_safety(ingredient.name)
                if ingredient.safety != safety or ingredient.note != note:
                    ingredient.safety = safety
                    ingredient.note = note
                    ingredient.save()
            clear_cache_for_detail(request, item_id)
            clear_cache_for_browse()
            messages.success(request, 'Item updated successfully!')
            return redirect('item:detail', pk=item.id)  # Redirect back to item detail after update
    else:
        form = NewItemForm(instance=item)

    return render(request, 'item/edit_item.html', {'form': form, 'item': item})
@login_required
def remove_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        clear_cache_for_browse()
        messages.success(request, 'Item deleted successfully!')
        return redirect('item:browse')
    return render(request, 'item/remove_item.html', {'item': item})