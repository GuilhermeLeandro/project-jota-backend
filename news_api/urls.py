from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Cria um router para registrar os ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'verticals', views.VerticalViewSet, basename='vertical')
router.register(r'plans', views.PlanViewSet, basename='plan')
router.register(r'user-plans', views.UserPlanViewSet, basename='userplan')
router.register(r'news', views.NewsViewSet, basename='news')

# As URLs da API são determinadas automaticamente pelo router.
urlpatterns = [
    path('', include(router.urls)),
]