from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm # Добавляем PasswordChangeForm для виджета
from django.contrib.auth.models import User
import re # Для валидации номера телефона
from .models import Point, Tag
import json # Импортируем json для парсинга тегов

class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя с верификацией email."""
    username = forms.CharField(
        label="Имя пользователя",
        max_length=150,
        required=True,
        help_text="Обязательно. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_."
    )
    email = forms.EmailField(
        required=True,
        help_text='Обязательное поле. Ваш email для входа и верификации.',
        label="Email"
    )
    # phone_number = forms.CharField(...) # Удалено поле телефона
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
        help_text="Минимум 8 символов. Не должен совпадать с именем пользователя или email. Не должен быть слишком простым или распространенным.",
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput,
        help_text="Введите тот же пароль, что и выше, для проверки."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Указываем поля в нужном порядке, исключая телефон
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.help_text:
                existing_attrs = field.widget.attrs
                existing_attrs['data-tippy-content'] = field.help_text
                field.widget.attrs = existing_attrs

    # def clean_phone_number(self): # Удален метод очистки телефона
    #     ...

    def clean_email(self):
        """Проверка уникальности email."""
        email = self.cleaned_data.get('email').lower()
        # Проверяем, есть ли уже активный пользователь или неактивный пользователь, ожидающий верификации
        if User.objects.filter(email=email).exists():
             # Дополнительно можно проверить, если email принадлежит неактивному пользователю,
             # можно ли ему перерегистрироваться или нужно восстановить пароль/верификацию.
             # Пока просто запрещаем дубликаты.
             raise forms.ValidationError("Пользователь с таким email уже зарегистрирован или ожидает верификации.")
        return email

class VerifyCodeForm(forms.Form):
    """Форма для ввода кода верификации (теперь для email)."""
    code = forms.CharField(
        max_length=6,
        required=True,
        label="Код верификации",
        widget=forms.TextInput(attrs={'autocomplete': 'off'}) # Отключаем автозаполнение
    )

class PointForm(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput())
    longitude = forms.FloatField(widget=forms.HiddenInput())
    address = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
        label="Адрес",
        required=False
    )
    point_type = forms.ChoiceField(
        choices=Point.POINT_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'}), # Используем Bootstrap класс form-select
        label="Тип точки",
        initial='event' # Устанавливаем начальное значение
    )
    # Убираем старые поля tags и new_tags
    # tags = forms.ModelMultipleChoiceField(...)
    # new_tags = forms.CharField(...)

    # Добавляем новое поле для ввода тегов (Tagify будет работать с ним)
    tags_input = forms.CharField(
        required=False,
        label="Теги",
        help_text="Введите теги. Существующие будут предложены. Несуществующие будут созданы.",
        # Пока оставляем TextInput, Tagify будет его использовать.
        # Можно сделать HiddenInput, если Tagify будет писать в него программно.
        widget=forms.TextInput(attrs={'class': 'form-control'}) # Дадим базовый класс
    )

    popup_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=False,
        label="Описание точки (необязательно)"
    )

    class Meta:
        model = Point
        # Обновляем список полей
        fields = ['latitude', 'longitude', 'address', 'point_type', 'tags_input', 'popup_text']

    def clean(self):
        cleaned_data = super().clean()
        # Валидация для tags_input (например, проверка формата JSON, если Tagify отдает JSON)
        tags_value = cleaned_data.get('tags_input')
        if tags_value:
            try:
                # Попытка парсинга как JSON (стандартный вывод Tagify)
                tags_list = json.loads(tags_value)
                if not isinstance(tags_list, list):
                    raise forms.ValidationError("Неверный формат тегов (ожидался список).")
                # Опционально: проверить структуру каждого элемента списка
                # for item in tags_list:
                #     if not isinstance(item, dict) or 'value' not in item:
                #        raise forms.ValidationError("Неверный формат элемента тега.")
            except json.JSONDecodeError:
                 # Если это не JSON, возможно, Tagify настроен отдавать строку с разделителями?
                 # Пока будем считать, что это ошибка, если не JSON.
                 # Если используется другой формат, нужно изменить логику парсинга здесь и в save().
                 # Можно просто оставить строку как есть, если парсить в save()
                pass # Пока пропускаем ошибку парсинга, будем обрабатывать в save()
            except Exception as e:
                 raise forms.ValidationError(f"Ошибка обработки тегов: {e}")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Сохраняем основной объект, если commit=True
        if commit:
            instance.save()

        # Обработка тегов из tags_input
        tags_json_string = self.cleaned_data.get('tags_input', '[]') # Получаем строку (по умолчанию пустой JSON массив)
        tag_objects = []
        try:
            tags_data = json.loads(tags_json_string) # Парсим JSON
            tag_names = [tag['value'].strip() for tag in tags_data if isinstance(tag, dict) and 'value' in tag and tag['value'].strip()]
        except json.JSONDecodeError:
             # Если не JSON, пробуем парсить как строку с запятыми (альтернативный вариант)
             print("Warning: Tag input was not valid JSON. Trying to parse as comma-separated.")
             tag_names = [name.strip() for name in tags_json_string.split(',') if name.strip()]
        except Exception as e:
            print(f"Error parsing tags: {e}. No tags will be saved.") # Логируем ошибку
            tag_names = []

        if tag_names:
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                tag_objects.append(tag)

        # Устанавливаем теги для instance, если commit=True
        if commit and tag_objects:
            instance.tags.set(tag_objects)
        elif commit: # Если тегов не было или произошла ошибка парсинга, очищаем связи
             instance.tags.clear()

        return instance