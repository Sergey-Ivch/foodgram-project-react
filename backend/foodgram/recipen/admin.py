from django.contrib import admin
from .models import Marks, Сomponents, The_chosen_one, Recipens
from . import models


class СomponentsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name', )
    search_fields = ('name', )

admin.site.register(Сomponents, СomponentsAdmin)

class MarksAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'

admin.site.register(Marks, MarksAdmin)

class RecipensAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'in_favorites', 'cooking_time', 'text', 'image')
    list_editable = ('name', 'cooking_time', 'text', 'image', 'author')
    empty_value_display = '-пусто-'
    
    @admin.display(description='В избранном')
    def in_favorites(self, obj):
        return obj.favorite_recipe.count()

admin.site.register(Recipens, RecipensAdmin)


@admin.register(models.Recipe_ingredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_editable = ('recipe', 'ingredient', 'amount')


class The_chosen_oneAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')

admin.site.register(The_chosen_one, The_chosen_oneAdmin)


@admin.register(models.Shopping_cart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')

