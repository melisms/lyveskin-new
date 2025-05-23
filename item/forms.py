from django import forms
from .models import Item, Ingredient, Category
from .utils import detect_safety

class NewItemForm(forms.ModelForm):
    ingredients_text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'input-classes'}),
        required=False,
        help_text="Enter ingredients separated by commas."
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            ingredients = ', '.join(ing.name for ing in self.instance.ingredients.all())
            self.initial['ingredients_text'] = ingredients
            self.initial_ingredients = ingredients
        else:
            self.initial_ingredients = ''

    class Meta:
        model = Item
        fields = ('category', 'brands', 'name', 'ingredients_text', 'description', 'image', 'skintype')
        widgets = {
            'category': forms.Select(attrs={'class': 'input-classes'}),
            'brands': forms.TextInput(attrs={'class': 'input-classes'}),
            'name': forms.TextInput(attrs={'class': 'input-classes'}),
            'description': forms.Textarea(attrs={'class': 'input-classes'}),
            'skintype': forms.TextInput(attrs={'class': 'input-classes'}),
            'image': forms.FileInput(attrs={'class': 'input-classes'}),
        }

    def save(self, commit=True):
        item = super().save(commit=False)
        item.save()
        def _normalize_ingredients(text):
            if not text:
                return set()
            return set(name.strip().lower() for name in text.split(','))
        new_ingredients_text = self.cleaned_data.get('ingredients_text', '').strip()
        new_ingredients_set = _normalize_ingredients(new_ingredients_text)
        initial_ingredients_set = _normalize_ingredients(self.initial_ingredients)
        if new_ingredients_set != initial_ingredients_set:
            item.ingredients.clear()
            formatted_names = {' '.join(word.capitalize() for word in name.split()) for name in new_ingredients_set}
            existing_ingredients = Ingredient.objects.filter(name__in=formatted_names)
            existing_names = set(ing.name for ing in existing_ingredients)
            names_to_create = formatted_names - existing_names
            new_ingredients = [Ingredient(name=name) for name in names_to_create]
            Ingredient.objects.bulk_create(new_ingredients)
            all_ingredients = list(Ingredient.objects.filter(name__in=formatted_names))
            to_update = []
            for ingredient in all_ingredients:
                if not ingredient.safety or ingredient.safety == 'N':
                    ingredient.safety = detect_safety(ingredient.name)
                    to_update.append(ingredient)
            if to_update:
                Ingredient.objects.bulk_update(to_update, ['safety'])
            item.save()  
            item.ingredients.add(*all_ingredients)

        elif commit:
            item.save()

        return item


class ComparisonForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="--- Select a category ---")
    item1 = forms.ModelChoiceField(
        queryset=Item.objects.filter(pk__isnull=False), 
        empty_label="--- Select an item ---",
        widget=forms.Select(attrs={'style': 'width: 200px;'}))
    item2 = forms.ModelChoiceField(
        queryset=Item.objects.filter(pk__isnull=False), 
        empty_label="--- Select an item ---",
        widget=forms.Select(attrs={'style': 'width: 200px;'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.is_bound:  # Check if form is submitted
            category_id = self.data.get('category')
            if category_id:
                try:
                    category = Category.objects.get(pk=category_id)
                    self.fields['item1'].queryset = Item.objects.filter(category=category)
                    self.fields['item2'].queryset = Item.objects.filter(category=category)
                except (ValueError, TypeError, Category.DoesNotExist):
                    pass
    
    def clean(self):
        cleaned_data = super().clean()
        # Optionally, add validation to ensure both items are selected
        item1 = cleaned_data.get('item1')
        item2 = cleaned_data.get('item2')
        if item1 and item2 and item1 == item2:
            raise forms.ValidationError("You cannot compare the same item twice.")
        return cleaned_data
