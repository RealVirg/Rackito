from django.db import models
from django.conf import settings

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
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")
    marker_image = models.ImageField(
        upload_to='map_markers/',
        verbose_name="Изображение маркера",
        help_text="Изображение, которое будет отображаться на карте для этой точки."
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True, # Можно не указывать теги
        related_name='points',
        verbose_name="Теги"
    )
    popup_text = models.TextField(
        blank=True,
        null=True,
        verbose_name="Текст для всплывающего окна",
        help_text="Текст, который будет показан при клике/наведении на точку."
    )

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
