from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Point, EmailVerification, Tag
import json
import random
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, VerifyCodeForm
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import login, get_user_model, authenticate, logout
from django.conf import settings # Импортируем settings
import requests # Импортируем requests для HTTP-запросов
User = get_user_model()

# Create your views here.

def index_view(request):
    """Отображает главную страницу (вход/регистрация)."""
    if request.user.is_authenticated:
        return redirect('RackitoMap:map_view')

    form = AuthenticationForm()
    return render(request, 'index.html', {'form': form})

def register_view(request):
    """Обработка регистрации нового пользователя с верификацией email."""
    if request.user.is_authenticated:
        return redirect('RackitoMap:map_view')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            email = form.cleaned_data['email']

            # Удаляем старые коды верификации для этого email, если есть
            EmailVerification.objects.filter(user=user).delete()

            # Генерируем код верификации
            verification_code = str(random.randint(100000, 999999))

            # Создаем запись верификации email
            EmailVerification.objects.create(
                user=user,
                code=verification_code
            )

            # ---- ЗАГЛУШКА ДЛЯ ОТПРАВКИ EMAIL ----
            print(f"\n--- КОД ВЕРИФИКАЦИИ EMAIL для {email}: {verification_code} ---\n")
            # ЗАМЕНИТЬ НА РЕАЛЬНУЮ ОТПРАВКУ EMAIL
            # send_mail('Код верификации Rackito', f'Ваш код: {verification_code}', 'from@example.com', [email])
            # -------------------------------------

            # Сохраняем ID пользователя в сессии для следующего шага
            request.session['verification_user_id'] = user.id
            messages.success(request, f'Регистрация почти завершена. Мы отправили код верификации на адрес {email}. Введите его ниже.')
            return redirect('verify_email') # Перенаправляем на страницу верификации email
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

def verify_email_view(request):
    """Обработка ввода кода верификации email."""
    user_id = request.session.get('verification_user_id')
    if not user_id:
        messages.error(request, 'Сессия верификации истекла или недействительна. Пожалуйста, начните регистрацию заново.')
        return redirect('register')

    try:
        # Ищем запись верификации по user_id
        verification = EmailVerification.objects.get(user_id=user_id)
        user = verification.user
    except EmailVerification.DoesNotExist:
        messages.error(request, 'Не найдена запись верификации. Пожалуйста, начните регистрацию заново.')
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

            if entered_code == verification.code:
                user.is_active = True
                user.save()
                verification.delete()
                if 'verification_user_id' in request.session:
                    del request.session['verification_user_id']
                login(request, user)
                messages.success(request, 'Email успешно подтвержден! Добро пожаловать!')
                return redirect('RackitoMap:map_view')
            else:
                messages.error(request, 'Неверный код верификации. Попробуйте еще раз.')
    else:
        form = VerifyCodeForm()

    context = {
        'form': form,
        'email': user.email # Передаем email пользователя
    }
    # Используем новый шаблон verify_email.html
    return render(request, 'registration/verify_email.html', context)

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

# Новая view для проксирования запроса обратного геокодирования
@login_required # Убедимся, что только авторизованные пользователи могут это делать
def reverse_geocode_proxy(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')

    if not lat or not lon:
        return HttpResponseBadRequest("Отсутствуют параметры 'lat' или 'lon'.")

    try:
        # Получаем ключ из настроек
        api_key = settings.LOCATIONIQ_API_KEY
        # Формируем URL для LocationIQ
        locationiq_url = f"https://us1.locationiq.com/v1/reverse.php?key={api_key}&lat={lat}&lon={lon}&format=json&accept-language=ru&addressdetails=1"

        # Делаем запрос к LocationIQ
        response = requests.get(locationiq_url, timeout=10) # Таймаут 10 секунд
        response.raise_for_status() # Вызовет исключение для плохих ответов (4xx или 5xx)

        # Возвращаем ответ от LocationIQ как JsonResponse
        # Важно: возвращаем именно json() ответа, а не весь объект response
        return JsonResponse(response.json())

    except requests.exceptions.RequestException as e:
        # Обработка ошибок сети или API
        print(f"Ошибка запроса к LocationIQ: {e}") # Логируем ошибку
        return JsonResponse({'error': 'Не удалось связаться с сервисом геокодирования.'}, status=503) # Service Unavailable
    except AttributeError:
        # Если LOCATIONIQ_API_KEY не найден в settings
        print("Ошибка: LOCATIONIQ_API_KEY не найден в настройках Django.")
        return JsonResponse({'error': 'Ошибка конфигурации сервера.'}, status=500)
    except Exception as e:
        # Обработка других непредвиденных ошибок
        print(f"Непредвиденная ошибка в reverse_geocode_proxy: {e}")
        return JsonResponse({'error': 'Внутренняя ошибка сервера.'}, status=500)

# --- Views для аутентификации --- #

@login_required
def get_tags_view(request):
    """Возвращает список существующих тегов для автодополнения."""
    if request.method == 'GET':
        query = request.GET.get('term', '') # 'term' используется многими библиотеками автодополнения
        tags = Tag.objects.filter(name__icontains=query).values_list('name', flat=True)[:10] # Ограничиваем 10 результатами
        return JsonResponse(list(tags), safe=False)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def create_point_view(request):
    """Создает новую точку на карте."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lat = data.get('lat')
            lon = data.get('lon')
            popup_text = data.get('popup_text', '')
            address = data.get('address', '')
            point_type = data.get('point_type', 'event') # Тип по умолчанию 'event'
            tag_names = data.get('tags', [])

            if lat is None or lon is None:
                return JsonResponse({'error': 'Missing latitude or longitude'}, status=400)

            # Обработка тегов: получаем существующие или создаем новые
            tags = []
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name.strip())
                tags.append(tag)

            # Создание точки
            # Пока не обрабатываем marker_image, предполагаем, что он будет зависеть от point_type
            point = Point.objects.create(
                latitude=lat,
                longitude=lon,
                popup_text=popup_text,
                address=address,
                point_type=point_type
                # marker_image будет обработан позже (например, во фронтенде по типу)
            )
            point.tags.set(tags)

            # Возвращаем данные созданной точки, включая теги
            # (можно использовать сериализатор, но пока сделаем вручную)
            response_data = {
                'id': point.id,
                'lat': point.latitude,
                'lon': point.longitude,
                'popup_text': point.popup_text,
                'address': point.address,
                'point_type': point.point_type,
                'tags': [tag.name for tag in point.tags.all()],
                'marker_icon_url': f"{settings.STATIC_URL}img/markers/{point.point_type}.png" # Формируем URL иконки на основе типа
            }
            return JsonResponse(response_data, status=201) # 201 Created

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            # Логируем ошибку
            print(f"Error creating point: {e}")
            return JsonResponse({'error': 'Failed to create point', 'details': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
