# Школьный фото-видео-аудио архив

Веб-приложение для хранения и организации школьных медиаматериалов.

## Функциональность
 - Загрузка фото, видео и аудио файлов
 - Категоризация по типам медиа
 - Администрирование каталогов и архивов
 - Поиск и фильтрация информации

## Технологии
 - Django 5.0
 - SQLite
 - HTML/CSS

## Установка
```bash
git clone https://github.com/PlayPit08/school_media_archive_g2.git
cd school_archive
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
