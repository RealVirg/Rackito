from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Point, PhoneVerification
import json
import random
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, VerifyCodeForm
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import login

# Create your views here.

def index_view(request):
    """Отображает главную страницу (вход/регистрация)."""
    if request.user.is_authenticated:
        return redirect('RackitoMap:map_view')

    form = AuthenticationForm()
    return render(request, 'index.html', {'form': form})

def register_view(request):
    """Обработка регистрации нового пользователя."""
    if request.user.is_authenticated:
        return redirect('RackitoMap:map_view')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Создаем пользователя, но пока не сохраняем в БД
            user = form.save(commit=False)
            # Делаем пользователя неактивным до верификации телефона
            user.is_active = False
            user.save() # Теперь сохраняем пользователя

            phone_number = form.cleaned_data['phone_number']

            # Удаляем старые коды верификации для этого номера, если есть
            PhoneVerification.objects.filter(phone_number=phone_number).delete()

            # Генерируем код верификации
            verification_code = str(random.randint(100000, 999999))

            # Создаем запись верификации
            PhoneVerification.objects.create(
                user=user,
                phone_number=phone_number,
                code=verification_code
            )

            # ---- ЗАГЛУШКА ДЛЯ ОТПРАВКИ SMS ----
            print(f"\n--- КОД ВЕРИФИКАЦИИ для {phone_number}: {verification_code} ---\n")
            # ЗАМЕНИТЬ НА РЕАЛЬНУЮ ОТПРАВКУ SMS ЧЕРЕЗ СЕРВИС
            # Например: send_sms(phone_number, f"Ваш код: {verification_code}")
            # -------------------------------------

            # Сохраняем ID пользователя в сессии для следующего шага
            request.session['verification_user_id'] = user.id
            messages.success(request, f'Регистрация почти завершена. Мы отправили код верификации на номер {phone_number}. Введите его ниже.')
            return redirect('verify_phone') # Перенаправляем на страницу верификации
        else:
            # Если форма невалидна, ошибки отобразятся в шаблоне
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

def verify_phone_view(request):
    """Обработка ввода кода верификации."""
    user_id = request.session.get('verification_user_id')
    if not user_id:
        messages.error(request, 'Сессия верификации истекла или недействительна. Пожалуйста, начните регистрацию заново.')
        return redirect('register') # Имя URL страницы регистрации

    try:
        verification = PhoneVerification.objects.get(user_id=user_id)
        user = verification.user
    except PhoneVerification.DoesNotExist:
        messages.error(request, 'Не найдена запись верификации. Пожалуйста, начните регистрацию заново.')
        # Очищаем сессию на всякий случай
        if 'verification_user_id' in request.session:
            del request.session['verification_user_id']
        return redirect('register')
    except User.DoesNotExist:
        messages.error(request, 'Пользователь для верификации не найден.')
        if 'verification_user_id' in request.session:
            del request.session['verification_user_id']
        return redirect('register')

    if request.method == 'POST':
        form = VerifyCodeForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['code']

            # Проверяем код
            if entered_code == verification.code:
                # Код верный, активируем пользователя
                user.is_active = True
                user.save()

                # Удаляем запись верификации
                verification.delete()

                # Очищаем ID из сессии
                if 'verification_user_id' in request.session:
                    del request.session['verification_user_id']

                # Осуществляем вход пользователя
                login(request, user)

                messages.success(request, 'Телефон успешно подтвержден! Добро пожаловать!')
                return redirect('RackitoMap:map_view') # Перенаправляем на карту
            else:
                messages.error(request, 'Неверный код верификации. Попробуйте еще раз.')
        # Если форма невалидна (например, пустое поле), ошибки покажутся в шаблоне
    else:
        form = VerifyCodeForm()

    # Передаем номер телефона в контекст, чтобы напомнить пользователю
    context = {
        'form': form,
        'phone_number': verification.phone_number
    }
    return render(request, 'registration/verify_phone.html', context)

def get_map_points_in_bounds(request):
    """Возвращает точки на карте, попадающие в заданные границы.

    Принимает GET-параметры: south, west, north, east (границы видимой области).
    Возвращает JSON со списком точек.
    """
    if request.method == 'GET':
        try:
            # Получаем границы из GET-параметров
            south = float(request.GET.get('south'))
            west = float(request.GET.get('west'))
            north = float(request.GET.get('north'))
            east = float(request.GET.get('east'))

            # Фильтруем точки, попадающие в прямоугольник границ
            # Обратите внимание: долгота может пересекать 180/-180 меридиан,
            # но для простоты пока считаем, что west < east.
            points = Point.objects.filter(
                latitude__gte=south,
                latitude__lte=north,
                longitude__gte=west,
                longitude__lte=east
            )

            # Сериализуем данные
            points_data = [
                {
                    'id': point.id,
                    'lat': point.latitude,
                    'lon': point.longitude,
                    'popup_text': point.popup_text or "", # Используем пустую строку, если текст null
                    'marker_icon_url': point.marker_image.url if point.marker_image else None # URL иконки
                }
                for point in points
            ]

            return JsonResponse(points_data, safe=False)

        except (TypeError, ValueError, AttributeError) as e:
            # Ошибка в параметрах или при доступе к данным
            return JsonResponse({'error': 'Invalid parameters or data error', 'details': str(e)}, status=400)
        except Exception as e:
            # Другие непредвиденные ошибки
            return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# View для отображения самой карты (требует логина)
@login_required(login_url='index')
def map_view(request):
    """Отображает страницу с картой."""
    # В будущем здесь можно передавать дополнительный контекст в шаблон,
    # например, список тегов для фильтрации или начальные настройки карты.
    context = {}
    return render(request, 'RackitoMap/map_template.html', context)
