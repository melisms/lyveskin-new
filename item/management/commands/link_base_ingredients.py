from django.core.management.base import BaseCommand
from item.models import Ingredient, BaseIngredient
from rapidfuzz import process

class Command(BaseCommand):
    help = "Link ingredients to their base ingredients using fuzzy matching"

    def handle(self, *args, **kwargs):
        base_names = list(BaseIngredient.objects.values_list('name', flat=True))

        count = 0
        for ingredient in Ingredient.objects.filter(base_ingredient__isnull=True):
            match, score, _ = process.extractOne(ingredient.name, base_names)
            if score >= 85:
                base = BaseIngredient.objects.get(name=match)
                ingredient.base_ingredient = base
                ingredient.save()
                count += 1
                self.stdout.write(f"Linked: {ingredient.name} -> {match} ({score})")
            else:
                self.stdout.write(f"No good match for: {ingredient.name} (best: {match}, score: {score})")
        self.stdout.write(f"\nLinked {count} ingredients.")
