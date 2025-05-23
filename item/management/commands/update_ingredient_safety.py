from django.core.management.base import BaseCommand
from item.models import Ingredient
from item.utils import detect_safety

class Command(BaseCommand):
    help = 'Update safety and notes for all existing Ingredients'

    def handle(self, *args, **kwargs):
        ingredients = Ingredient.objects.all()
        total = ingredients.count()
        self.stdout.write(f"Updating safety info for {total} ingredients...")

        for ingredient in ingredients:
            safety, note = detect_safety(ingredient.name)
            if ingredient.safety != safety or ingredient.note != note:
                ingredient.safety = safety
                ingredient.note = note
                ingredient.save()
                self.stdout.write(f"Updated {ingredient.name}: Safety={safety}, Note={note}")
            else:
                self.stdout.write(f"No change for {ingredient.name}")

        self.stdout.write("Update complete.")
