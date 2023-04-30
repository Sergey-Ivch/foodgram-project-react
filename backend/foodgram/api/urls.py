from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from api.views import BuyerList, BuyersList, user_me, set_password, MarksList, MarksRetrieve, UserViewSet, СomponentsList, СomponentsRetrieve
from . import views

router = DefaultRouter()
router.register(r'api/recipes', views.RecipeViewSet, basename='recipes')
router.register(r'api/users(?!/me/|/[0-9]/$|/set_password|/$)', views.UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('api/users', BuyerList.as_view()),
    path('api/users/<int:pk>/', BuyersList.as_view()),
    path('api/users/me/', user_me),
    path('api/users/set_password/', set_password),
    path('api/tags/', MarksList.as_view()),
    path('api/tags/<int:pk>/', MarksRetrieve.as_view()),
    path(r'auth/', include('djoser.urls.authtoken')),
    path('api/ingredients/', СomponentsList.as_view()),
    path('api/ingredients/<int:pk>/', СomponentsRetrieve.as_view()),
]
