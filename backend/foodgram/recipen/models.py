from django.core.validators import MinValueValidator
from django.db import models
from users.models import Buyer
from .validators import validate_hex


class Сomponents(models.Model):
    name = models.CharField('Название', max_length=150)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    def __str__(self):
        return f"{self.name} {self.measurement_unit}" 


class Marks(models.Model):
    name = models.CharField('Название',max_length = 150)

    color = models.CharField(
        'Шестнадцатеричная система цветов',
        max_length=7,
        null=True,
        validators=[validate_hex]  
    )
    slug = models.SlugField('Уникальное значение',
        max_length=150,
        unique=True,
        null=True,
        blank=False
    )

    def __str__(self):
        return self.name


class Recipens(models.Model):
    class Meta:
        verbose_name = 'Рецепт'

    name = models.CharField('Название', max_length=200)
    text = models.TextField('Описание', max_length = 300)
    cooking_time = models.IntegerField('Время приготовления, мин')
    image = models.ImageField('Картинка',upload_to='recipes/',blank=True)
    pub_date = models.DateTimeField('Дата публикации',auto_now_add=True)
    author = models.ForeignKey(
        Buyer, on_delete=models.CASCADE, related_name='recipe')
    ingredients = models.ManyToManyField(
        Сomponents, through='Recipe_ingredient')
    tags = models.ManyToManyField(Marks)

    def __str__(self):
        return self.name


class Recipe_ingredient(models.Model):
    class Meta:
        unique_together = ('recipe', 'ingredient') 

    recipe = models.ForeignKey(
        Recipens, on_delete=models.CASCADE, related_name='recipes')
    ingredient = models.ForeignKey(
        Сomponents, on_delete=models.CASCADE, related_name='ingredients')
    amount = models.IntegerField('Количество')

    def __str__(self):
        return (f'{self.recipe.name}{self.ingredient.cool}'
                f'{self.amount}{self.ingredient.measurement_unit}')


class The_chosen_one(models.Model):
    class Meta:
       unique_together = ('user', 'recipe') 

    user = models.ForeignKey(
        Buyer, on_delete=models.CASCADE, related_name='favorite_user')
    recipe = models.ForeignKey(
        Recipens, on_delete=models.CASCADE, related_name='favorite_recipe')

    def __str__(self):
        return f"{self.user.username} {self.recipe.name}"

class Shopping_cart(models.Model):
    class Meta:
       unique_together = ('user', 'recipe') 

    user = models.ForeignKey(
        Buyer, on_delete=models.CASCADE,related_name='shopping_user')
    recipe = models.ForeignKey(
        Recipens, on_delete=models.CASCADE, related_name='shopping_recipe')

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
