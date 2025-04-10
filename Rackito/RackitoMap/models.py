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

class PhoneVerification(models.Model):
    """Модель для хранения кодов верификации по номеру телефона."""
    # Связываем с пользователем, который регистрируется
    # Используем AUTH_USER_MODEL для гибкости
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='phone_verification'
    )
    phone_number = models.CharField(
        max_length=20,
        unique=True, # Один номер - один код (до верификации)
        verbose_name="Номер телефона"
    )
    code = models.CharField(max_length=6, verbose_name="Код верификации")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    # Можно добавить поле is_verified, если нужно хранить факт верификации
    # Или просто удалять запись после успешной верификации

    def __str__(self):
        return f"Верификация для {self.user.username} ({self.phone_number})"

    class Meta:
        verbose_name = "Верификация телефона"
        verbose_name_plural = "Верификации телефонов"
        # Индекс для быстрого поиска по телефону
        indexes = [models.Index(fields=['phone_number'])]
