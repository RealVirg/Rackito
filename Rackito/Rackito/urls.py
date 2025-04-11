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
from RackitoMap.views import index_view, register_view, verify_email_view
# Импортируем стандартные представления аутентификации
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # URL для аутентификации (login, logout, password_reset, etc.)
    # Используем стандартный LoginView для обработки /accounts/login/
    # Указываем ему использовать наш шаблон index.html
    path('accounts/login/', auth_views.LoginView.as_view(template_name='index.html'), name='login'),
    # Подключаем остальные стандартные URL аутентификации (logout, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # URL регистрации и верификации
    path('register/', register_view, name='register'),
    path('verify-email/', verify_email_view, name='verify_email'),

    # URL приложения карты
    path('app/', include('RackitoMap.urls')), # Подключает /map/ и /map/points/

    # Корневой URL ведет на страницу входа/регистрации (отображается через index_view)
    path('', index_view, name='index'),
]

# Добавляем обработку медиафайлов для режима разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
