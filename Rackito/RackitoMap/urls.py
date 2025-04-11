from django.urls import path
from . import views

app_name = 'RackitoMap' # Добавляем пространство имен

urlpatterns = [
    # Этот URL теперь будет корневым для всего сайта, см. основной urls.py
    # path('', views.index_view, name='index'),
    # URL для отображения карты (требует логина)
    path('map/', views.map_view, name='map_view'),
    # URL для получения точек (API, также может потребовать login_required в будущем)
    path('map/points/', views.get_map_points_in_bounds, name='get_map_points'),
    # Возможно, главный URL для отображения самой карты?
    # path('', views.map_view, name='map_view'), # Раскомментируйте и создайте view, если нужно
    # Добавляем новый URL для обратного геокодирования
    path('reverse-geocode/', views.reverse_geocode_proxy, name='reverse_geocode_proxy'),
] 