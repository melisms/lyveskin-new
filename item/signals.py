import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Item, Ingredient

logger = logging.getLogger(__name__)



@receiver(post_save, sender=Item)
def add_ingredients(sender, instance, created, **kwargs):
    if created:
        logger.info("Item created: %s", instance.name)
        ingredients = instance.ingredients.all()  # Get related ingredients directly
        if ingredients:
            added_ingredients = set()  # Set to keep track of added ingredients
            for ingredient in ingredients:
                logger.debug("Original ingredient name: %s", ingredient.name)
                # Format ingredient name to title case without capitalizing
                formatted_name = ' '.join(word.strip().capitalize() for word in ingredient.name.split(','))
                logger.debug("Formatted ingredient name: %s", formatted_name)
                # Check if the ingredient with the formatted name already exists
                existing_ingredient = Ingredient.objects.filter(name=formatted_name).first()
                if existing_ingredient:
                    instance.ingredients.remove(ingredient)  # Remove duplicate ingredient
                    logger.debug("Duplicate ingredient removed: %s", ingredient.name)
                else:
                    if formatted_name not in added_ingredients:
                        added_ingredients.add(formatted_name)
                    else:
                        instance.ingredients.remove(ingredient)  # Remove duplicate ingredient
                        logger.debug("Duplicate ingredient removed: %s", ingredient.name)