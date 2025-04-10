"""Rackito URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
# Импортируем views
from RackitoMap.views import index_view, register_view, verify_phone_view

urlpatterns = [
    path('admin/', admin.site.urls),
    # URL для аутентификации (login, logout, password_reset, etc.)
    # Заменяем стандартный login своим index_view
    # Стандартный logout и другие можно оставить
    path('accounts/login/', index_view, name='login'), # Переопределяем login
    path('accounts/', include('django.contrib.auth.urls')),

    # URL регистрации и верификации
    path('register/', register_view, name='register'),
    path('verify-phone/', verify_phone_view, name='verify_phone'),

    # URL приложения карты
    path('', include('RackitoMap.urls')), # Подключает /map/ и /map/points/

    # Корневой URL ведет на страницу входа/регистрации
    path('', index_view, name='index'),
]

# Добавляем обработку медиафайлов для режима разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
