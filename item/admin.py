from django.contrib import admin

from .models import Category, Item, Ingredient, BaseIngredient

admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Ingredient)
admin.site.register(BaseIngredient)
# Register your models here.
