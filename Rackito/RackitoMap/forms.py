from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re # Для валидации номера телефона

class UserRegistrationForm(UserCreationForm):
    """Форма регистрации пользователя с добавлением номера телефона."""
    # Переопределяем email, чтобы сделать его обязательным
    email = forms.EmailField(required=True, help_text='Обязательное поле. Ваш email.')
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        help_text='Обязательное поле. Введите номер телефона (например, +79XXXXXXXXX).',
        label="Номер телефона"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Включаем стандартные поля + наши новые
        fields = UserCreationForm.Meta.fields + ('email', 'phone_number')

    def clean_phone_number(self):
        """Проверка формата номера телефона."""
        phone = self.cleaned_data.get('phone_number')
        # Простая регулярка для примера (можно усложнить)
        # Убираем все не-цифры, кроме начального плюса
        cleaned_phone = re.sub(r'[^\d+]', '', phone)
        if not re.match(r'^\+?\d{10,15}$', cleaned_phone):
            raise forms.ValidationError("Неверный формат номера телефона.")

        # Проверяем, не занят ли номер уже активным пользователем
        # (мы позволим использовать номер, если пользователь неактивен/не верифицирован)
        # Также проверяем, не существует ли уже запись верификации для этого номера
        from .models import PhoneVerification # Импорт здесь во избежание циклического импорта
        if User.objects.filter(phone_verification__phone_number=cleaned_phone, is_active=True).exists() or \
           PhoneVerification.objects.filter(phone_number=cleaned_phone).exists():
             raise forms.ValidationError("Этот номер телефона уже используется или ожидает верификации.")

        return cleaned_phone

    def clean_email(self):
        """Проверка уникальности email."""
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

class VerifyCodeForm(forms.Form):
    """Форма для ввода кода верификации."""
    code = forms.CharField(
        max_length=6,
        required=True,
        label="Код верификации",
        widget=forms.TextInput(attrs={'autocomplete': 'off'}) # Отключаем автозаполнение
    )