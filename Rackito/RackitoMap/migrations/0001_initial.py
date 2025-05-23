# Generated by Django 4.2.20 on 2025-04-11 04:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Название тега')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField(verbose_name='Широта')),
                ('longitude', models.FloatField(verbose_name='Долгота')),
                ('marker_image', models.ImageField(help_text='Изображение, которое будет отображаться на карте для этой точки.', upload_to='map_markers/', verbose_name='Изображение маркера')),
                ('popup_text', models.TextField(blank=True, help_text='Текст, который будет показан при клике/наведении на точку.', null=True, verbose_name='Текст для всплывающего окна')),
                ('tags', models.ManyToManyField(blank=True, related_name='points', to='RackitoMap.tag', verbose_name='Теги')),
            ],
            options={
                'verbose_name': 'Точка на карте',
                'verbose_name_plural': 'Точки на карте',
            },
        ),
        migrations.CreateModel(
            name='PhoneVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=20, unique=True, verbose_name='Номер телефона')),
                ('code', models.CharField(max_length=6, verbose_name='Код верификации')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='phone_verification', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Верификация телефона',
                'verbose_name_plural': 'Верификации телефонов',
                'indexes': [models.Index(fields=['phone_number'], name='RackitoMap__phone_n_9187fe_idx')],
            },
        ),
    ]
