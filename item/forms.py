from django import forms
from .models import Item, Ingredient, Category

class NewItemForm(forms.ModelForm):
    ingredients_text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'input-classes'}),
        required=False,
        help_text="Enter ingredients separated by commas."
    )

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
        item.save()  # Save the item first to generate the primary key (id)
        ingredients_text = self.cleaned_data['ingredients_text']
        if ingredients_text:
            ingredient_names = [name.strip() for name in ingredients_text.split(',')]
            for name in ingredient_names:
                ingredient, created = Ingredient.objects.get_or_create(name=name)
                item.ingredients.add(ingredient)
        if commit:
            item.save()
        return item


class ComparisonForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label=None)
    item1 = forms.ModelChoiceField(queryset=Item.objects.filter(pk__isnull=False), empty_label=None,
                                   widget=forms.Select(attrs={'style': 'width: 200px;'}))
    item2 = forms.ModelChoiceField(queryset=Item.objects.filter(pk__isnull=False), empty_label=None,
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

