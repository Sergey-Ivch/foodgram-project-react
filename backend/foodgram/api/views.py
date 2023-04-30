from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import Buyer, Signer
from recipen.models import Marks, Recipens, Сomponents, The_chosen_one, Shopping_cart, Recipe_ingredient
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .pagination import CustomPaginator
from .serializers import (BuyerSerializer, 
                  BuyersSerializer, SetPasswordSerializer, MarksSerializer, 
                  RecipeReadSerializer, RecipeCreateSerializer, SignerSerializer,
                  SignerAuthSerializer, СomponentsSerializer, RecipeSerializer)
from django.db.models import Sum
from django.http import HttpResponse
from foodgram.settings import NAME


class BuyerList(generics.ListCreateAPIView):
    queryset = Buyer.objects.all()
    serializer_class = BuyerSerializer()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BuyersSerializer
        return BuyerSerializer

class BuyersList(generics.RetrieveAPIView):
    queryset = Buyer.objects.all()
    serializer_class = BuyersSerializer


@api_view(['GET'])
def user_me(request):
    Buyers = Buyer.objects.all()
    serializer = BuyersSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])  
def set_password(request):
    serializer = SetPasswordSerializer(request.user, data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response({serializer.data['new_password']: 'Ваш новый пароль для текущего пользователя.'})


class MarksList(generics.ListAPIView):
    queryset = Marks.objects.all()
    serializer_class = MarksSerializer


class MarksRetrieve(generics.RetrieveAPIView):
    queryset = Marks.objects.all()
    serializer_class = MarksSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipens.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
       if self.action in ('list', 'retrieve'):
           return RecipeReadSerializer
       return RecipeCreateSerializer
    
    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        if request.method == 'POST':
            serializer = RecipeSerializer(get_object_or_404(Recipens, id=kwargs['pk']),
                                          data=request.data,
                                          context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not The_chosen_one.objects.filter(user=request.user,
                                     recipe=get_object_or_404(Recipens, id=kwargs['pk'])).exists():
                The_chosen_one.objects.create(user=request.user, 
                                     recipe=get_object_or_404(Recipens, id=kwargs['pk']))
                return Response(serializer.data)
            else:
                return Response({'errors': 'Рецепт уже там.'})

        if request.method == 'DELETE':
            get_object_or_404(The_chosen_one, user=request.user,
                              recipe=get_object_or_404(Recipens, id=kwargs['pk'])).delete()
            return Response({'detail': 'Рецепт успешно удален из избранного.'})
    
    
    @action(detail=True, methods=['post', 'delete'], permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        if request.method == 'POST':
            serializer = RecipeSerializer(get_object_or_404(Recipens, id=kwargs['pk']),data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not Shopping_cart.objects.filter(user=request.user,
                                                recipe=get_object_or_404(Recipens,
                                                id=kwargs['pk'])).exists():
                Shopping_cart.objects.create(user=request.user,
                                             recipe=get_object_or_404(Recipens, id=kwargs['pk']))
                return Response(serializer.data)
            return Response({'errors': 'Рецепт уже в списке покупок.'})

        if request.method == 'DELETE':
            get_object_or_404(Shopping_cart, user=request.user,
                              recipe=get_object_or_404(Recipens, id=kwargs['pk'])).delete()
            return Response(
                {'detail': 'Рецепт убран из списка покупок.'})

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        file_list = []
        for func_componets in (Recipe_ingredient.objects.filter(
                               recipe__shopping_recipe__user=request.user).values('ingredient')
                               .annotate(total_amount=Sum('amount')).values_list('ingredient__name', 'total_amount',
                               'ingredient__measurement_unit')):

            file_list.append('{} - {} {}.'.format(*func_componets)) 
        file = HttpResponse('Cписок ингредиентов:\n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = (f'attachment; filename={NAME}')
        return file


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = Buyer.objects.all()

    @action(detail=True, methods=['post', 'delete'], permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):

        if request.method == 'DELETE':
            get_object_or_404(Signer, user=request.user, author=get_object_or_404(Buyer, id=kwargs['pk'])).delete()
            return Response({'detail': 'Вы успешно отписались от автора постов'})
        
        if request.method == 'POST':
            serializer = SignerAuthSerializer(
                get_object_or_404(Buyer, id=kwargs['pk']), data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            Signer.objects.create(user=request.user, author=get_object_or_404(Buyer, id=kwargs['pk']))
            return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        queryset = Buyer.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SignerSerializer(page, many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)
    

class СomponentsList(generics.ListAPIView):
    queryset = Сomponents.objects.all()
    serializer_class = СomponentsSerializer


class СomponentsRetrieve(generics.RetrieveAPIView):
    queryset = Сomponents.objects.all()
    serializer_class = СomponentsSerializer



