from django.db import models
from django.conf import settings
from django.templatetags.static import static # Импортируем static

# Create your models here.

class Tag(models.Model):
    """Модель для тегов точек на карте."""
    name = models.CharField(max_length=50, unique=True, verbose_name="Название тега")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

class Point(models.Model):
    """Модель для точки на карте."""
    POINT_TYPES = [
        ('event', 'Событие'),
        # Добавьте сюда другие типы по необходимости
        # ('place', 'Место'),
    ]

    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")
    tags = models.ManyToManyField(
        Tag,
        blank=True, # Можно не указывать теги
        related_name='points',
        verbose_name="Теги"
    )
    point_type = models.CharField(
        max_length=50,
        choices=POINT_TYPES,
        default='event',
        verbose_name="Тип точки",
        help_text="Тип метки на карте (например, событие, место)."
    )
    popup_text = models.TextField(
        blank=True,
        null=True,
        verbose_name="Текст для всплывающего окна",
        help_text="Текст, который будет показан при клике/наведении на точку."
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Адрес",
        help_text="Адрес, полученный с помощью обратного геокодирования."
    )

    def get_icon_url(self):
        """Возвращает URL иконки маркера.

        Приоритет у загруженного изображения. Если его нет,
        возвращает путь к статической иконке на основе типа точки.
        """
        if self.marker_image:
            return self.marker_image.url
        else:
            # Словарь соответствия типов иконок статическим файлам
            type_icons = {
                'event': 'img/markers/event.png',
                # Добавь сюда другие типы и пути к их иконкам
                # 'place': 'img/markers/place.png',
            }
            # Получаем путь к иконке для текущего типа или используем дефолтную, если тип неизвестен
            icon_path = type_icons.get(self.point_type, 'img/markers/default.png') # Нужна default.png!
            try:
                return static(icon_path)
            except ValueError: # На случай, если static() не может найти файл
                print(f"Warning: Static file not found for icon path: {icon_path}")
                # Можно вернуть URL к базовой дефолтной иконке Leaflet или None
                return None # Или static('img/markers/default.png') если она точно есть

    def __str__(self):
        return f"Точка ({self.latitude}, {self.longitude})"

    class Meta:
        verbose_name = "Точка на карте"
        verbose_name_plural = "Точки на карте"

# Модель PhoneVerification удалена
# class PhoneVerification(models.Model):
#     ...

# Добавляем модель EmailVerification
class EmailVerification(models.Model):
    """Модель для хранения кодов верификации по email."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_verification'
    )
    code = models.CharField(max_length=6, verbose_name="Код верификации")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    def __str__(self):
        return f"Верификация Email для {self.user.username}"

    class Meta:
        verbose_name = "Верификация Email"
        verbose_name_plural = "Верификации Email"

# Не забудьте создать и применить миграции:
# python manage.py makemigrations RackitoMap
# python manage.py migrate
