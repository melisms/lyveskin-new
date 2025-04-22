from django.contrib import admin

from .models import Category, Item, Ingredient

admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Ingredient)
# Register your models here.
