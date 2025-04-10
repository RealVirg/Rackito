#!/bin/sh

# Создать миграции, если они нужны
echo "Making migrations..."
python manage.py makemigrations --noinput

# Выполнить миграции базы данных
echo "Applying database migrations..."
python manage.py migrate --noinput

# Собрать статические файлы
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Запустить основной процесс (переданный через CMD)
exec "$@" 