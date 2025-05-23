from django.db import models
from .utils import detect_safety

class Category(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    safety = models.CharField(
        choices=(('S', "Safe"),
                ('N', "Neutral"),
                ('R', "Risky"),
                ),max_length=1,default='N',blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    def save(self, *args, **kwargs):
        if not self.safety or self.safety == 'N':
            result = detect_safety(self.name)
            if isinstance(result, tuple) and len(result) == 2:
                self.safety, self.note = result
            else:
                self.safety = result
                self.note = ''
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name

class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='items_images/', blank=True, null=True)
    ingredients = models.ManyToManyField(Ingredient)
    brands = models.CharField(max_length=200, blank=True, null=True)
    skintype = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return (self.brands or '') + ' ' + self.name

    def calculate_health_score(self):
        ingredients = self.ingredients.all()
        safe_count = ingredients.filter(safety='S').count()
        risky_count = ingredients.filter(safety='R').count()
        total_count = safe_count + risky_count

        if total_count == 0:
            return {'score': 100, 'safe': 0, 'risky': 0}

        score = (safe_count / total_count) * 100

        score = round(score)

        return {
            'score': score,
            'safe': safe_count,
            'risky': risky_count,
        }
    