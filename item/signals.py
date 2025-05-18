import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Item, Ingredient
from users.models import UserProfile 

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Item)
def add_ingredients(sender, instance, created, **kwargs):
    if created:
        logger.info("Item created: %s", instance.name)
        ingredients = instance.ingredients.all()
        if ingredients:
            added_ingredients = set()
            for ingredient in ingredients:
                logger.debug("Original ingredient name: %s", ingredient.name)
                formatted_name = ' '.join(word.strip().capitalize() for word in ingredient.name.split(','))
                logger.debug("Formatted ingredient name: %s", formatted_name)

                existing_ingredient = Ingredient.objects.filter(name=formatted_name).first()
                if existing_ingredient:
                    instance.ingredients.remove(ingredient)
                    logger.debug("Duplicate ingredient removed: %s", ingredient.name)
                else:
                    if formatted_name not in added_ingredients:
                        added_ingredients.add(formatted_name)
                    else:
                        instance.ingredients.remove(ingredient)
                        logger.debug("Duplicate ingredient removed: %s", ingredient.name)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)



