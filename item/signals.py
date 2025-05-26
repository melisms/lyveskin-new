import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Item, Ingredient
from users.models import UserProfile
from django.db.models.signals import m2m_changed
from .utils import detect_safety 

logger = logging.getLogger(__name__)

_in_signal_processing = set()
@receiver(m2m_changed, sender=Item.ingredients.through)
def format_and_check_ingredients(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action != 'post_add':
        return
    if instance.pk in _in_signal_processing:
            return
    _in_signal_processing.add(instance.pk)
    try:
        logger.info("Ingredients added to item: %s", instance.name)
        ingredient_map = {ing.pk: ing for ing in Ingredient.objects.filter(pk__in=pk_set)}
        formatted_names = set()

        for pk in pk_set:
            ingredient = ingredient_map[pk]
            original_name = ingredient.name
            formatted_name = ' '.join(word.strip().capitalize() for word in original_name.split())
            existing = Ingredient.objects.filter(name=formatted_name).exclude(pk=ingredient.pk).first()

            if existing or formatted_name in formatted_names:
                instance.ingredients.remove(ingredient)
                if existing:
                    instance.ingredients.add(existing)
                    logger.debug("Replaced duplicate ingredient '%s' with existing formatted '%s'", original_name, formatted_name)
                else:
                    logger.debug("Duplicate already processed: %s", formatted_name)
                continue
            if ingredient.name != formatted_name:
                new_ingredient, created = Ingredient.objects.get_or_create(name=formatted_name)
                if created or not new_ingredient.safety or new_ingredient.safety == 'N':
                    safety, note = detect_safety(formatted_name)
                    new_ingredient.safety = safety
                    new_ingredient.note = note
                    new_ingredient.save()
                instance.ingredients.remove(ingredient)
                instance.ingredients.add(new_ingredient)
                logger.debug("Cloned and replaced ingredient '%s' with formatted '%s'", original_name, formatted_name)
                formatted_names.add(formatted_name)
            else:
                if not ingredient.safety or ingredient.safety == 'N':
                    safety, note = detect_safety(formatted_name)
                    ingredient.safety = safety
                    ingredient.note = note
                    ingredient.save()
                    logger.debug("Updated safety for existing ingredient: %s", formatted_name)
                formatted_names.add(formatted_name)
    finally:
        _in_signal_processing.remove(instance.pk)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)



