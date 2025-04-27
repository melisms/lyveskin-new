from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=50)
    safety = models.CharField(
        choices=(('S', "Safe"),
                ('N', "Neutral"),
                ('R', "Risky"),
                ),max_length=1,default='N',blank=True, null=True)


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
        return self.brands+' '+self.name

    def calculate_health_score(self):
        ingredients = self.ingredients.all()
        safe_count = ingredients.filter(safety='S').count()
        risky_count = ingredients.filter(safety='R').count()
        total_count = safe_count + risky_count

        if total_count == 0:
            return {'score': 100, 'safe': 0, 'risky': 0}

        risky_percentage = (risky_count / total_count) * 100

        if risky_percentage == 0:
            score = 100
        elif risky_percentage <= 20:
            score = 80
        elif risky_percentage <= 50:
            score = 60
        else:
            score = 40

        return {
            'score': score,
            'safe': safe_count,
            'risky': risky_count,
        }
    