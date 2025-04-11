from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm # Добавляем PasswordChangeForm для виджета
from django.contrib.auth.models import User
import re # Для валидации номера телефона

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