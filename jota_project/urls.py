"""
URL configuration for jota_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # URLs da API da news_api (prefixadas com /api/)
    path('api/', include('news_api.urls')),

    # URLs de Autenticação JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Para obter access e refresh tokens
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Para obter um novo access token usando o refresh token

    # Incluir URLs de login/logout do DRF (opcional, útil para navegar na API pelo browser)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)