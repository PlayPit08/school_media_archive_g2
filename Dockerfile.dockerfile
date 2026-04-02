# Используем официальный образ Python
FROM python:3.10-slim

# Отключаем буферизацию вывода Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    gcc \
    libdbus-1-dev \
    libgirepository1.0-dev \
    libcairo2-dev \
    libglib2.0-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libcups2-dev \
    libsystemd-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем директорию для статических файлов
RUN mkdir -p /app/staticfiles

# Выполняем миграции и собираем статику при запуске контейнера
# (это будет происходить каждый раз при старте)
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]