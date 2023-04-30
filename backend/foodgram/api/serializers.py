from django.core import exceptions as django_exceptions
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from users.models import Signer, Buyer
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from recipen.models import (The_chosen_one, Сomponents, Recipens, Recipe_ingredient,
                            Shopping_cart, Marks)
from djoser.serializers import UserCreateSerializer, UserSerializer

class BuyerSerializer(UserSerializer):
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = Buyer
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class BuyersSerializer(UserCreateSerializer):
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Buyer
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')
    
    def get_is_subscribed(self, obj):
        content = self.context.get('request')
        if (content and not self.context['request'].user.is_anonymous):
            return Signer.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        return False

class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=150)
    new_password = serializers.CharField(max_length=150)

    def update(self, instance, validated_data):
        current_password = validated_data.get('current_password')
        new_password = validated_data.get('new_password')

        if current_password == new_password:
            raise serializers.ValidationError(
                {new_password: 'новый пароль не должен совпадать с текущим.'}
            )

        elif instance.check_password(current_password) == False:
            raise serializers.ValidationError(
                {current_password: 'Неправильный пароль.'}
            )
        else:
            instance.set_password(new_password)
            instance.save()
            return validated_data

    def validate(self, data):
        if data['new_password'].isdigit() == True:
            raise serializers.ValidationError(
                'Введённый новый пароль состоит только из цифр.')

        elif len(data['new_password']) < 8:
            raise serializers.ValidationError(
                'Введённый новый пароль слишком короткий. Он должен содержать как минимум 8 символов.')

        elif data['new_password'][0].isupper() == False:
            raise serializers.ValidationError(
                'Введённый новый пароль не имеет заглавной буквы.')

        return super().validate(data)


class MarksSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100)
    class Meta:
        model = Marks
        fields = ('id', 'name', 'color', 'slug')

class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(
                       source='ingredient.measurement_unit')
    name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        model = Recipe_ingredient
        fields = ('id', 'name','measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = BuyersSerializer(read_only=True)
    tags = MarksSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source='recipes')
    is_favorited, is_in_shopping_cart = serializers.SerializerMethodField(), serializers.SerializerMethodField()


    def get_is_favorited(self, obj):
        auth_user = self.context.get('request').user.is_authenticated
        current_user = self.context.get('request').user
        return(auth_user and The_chosen_one.objects.filter(user=current_user,
                                        recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        auth_user = self.context.get('request').user.is_authenticated
        current_user = self.context.get('request').user
        return(auth_user and Shopping_cart.objects.filter(user=current_user,
                                        recipe=obj).exists())
    
    class Meta:
        model = Recipens
        fields = ('id', 'tags','author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image','text', 'cooking_time')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Recipe_ingredient
        exclude = ('recipe', 'ingredient')


class RecipeSerializer(serializers.ModelSerializer):
    """Список рецептов без ингридиентов."""
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipens
        fields = ('id', 'name',
                  'image', 'cooking_time')


class RecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    tags = serializers.PrimaryKeyRelatedField(queryset=Marks.objects.all(), many=True)
    author = BuyersSerializer(read_only=True)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipens
        fields = ('id', 'ingredients',
                  'tags', 'image',
                  'name', 'text',
                  'cooking_time', 'author')

    def validate(self, object):
        if not object.get('tags'):
            raise serializers.ValidationError('у вас нет Тегов.')
        if not object.get('ingredients'):
            raise serializers.ValidationError('у вас нет ингредиентов.')
        return object
    
    def tag_disclosure(self, recipe, Marks, Сomponented):
        recipe.tags.set(Marks)
        for ingredient in Сomponented:
            Recipe_ingredient.objects.bulk_create([Recipe_ingredient(recipe=recipe,
                                                   ingredient=Сomponents.objects.get(pk=ingredient['id']),
                                                   amount=ingredient['amount'])])

    def create(self, validated_data):
        Marks, Сomponented = validated_data.pop('tags'), validated_data.pop('ingredients')
        recipe = Recipens.objects.create(author=self.context['request'].user,
                                       **validated_data)
        self.tag_disclosure(recipe, Marks, Сomponented)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time) 
        instance.text = validated_data.get('text', instance.text)
        Marks = validated_data.pop('tags')
        Сomponented = validated_data.pop('ingredients')
        Recipe_ingredient.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        self.tag_disclosure(instance, Marks, Сomponented)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance,
                                    context=self.context).data


class SignerSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Buyer
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_recipes(self, objects):
        serializer = RecipeSerializer(objects.recipe.all()[:4], many=True, read_only=True)
        return serializer.data

    def get_is_subscribed(self, objects):
        current_user = self.context.get('request').user
        return (
                current_user.is_authenticated and 
                Signer.objects.filter(user=current_user, author=objects).exists()
        )

    def get_recipes_count(self, objects):
        return objects.recipe.count()


class SignerAuthSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()

    class Meta:
        model = Buyer
        fields = ('email', 'id', 'username', 'first_name','last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def validate(self, objects):
        if (self.context['request'].user == objects):
            raise serializers.ValidationError({'errors': 'На себя подписаться нельзя.'})
        return objects

    def get_is_subscribed(self, object):
        auth_user = self.context.get('request').user.is_authenticated
        return (auth_user and Signer.objects.filter(user=self.context['request'].user,
                                          author=object).exists()
        )

    def get_recipes_count(self, objects):
        return objects.recipe.count()



class СomponentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Сomponents
        fields = ('id', 'name', 'measurement_unit')


    
