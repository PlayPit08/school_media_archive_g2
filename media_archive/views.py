from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import YearAlbum, SchoolClass, EventAlbum, Photo
from .forms import YearAlbumForm, SchoolClassForm, EventAlbumForm, PhotoUploadForm

# Главная страница - показываем только одобренные учебные годы
def home(request):
    # Для админов показываем все годы, для остальных - только approved
    if request.user.is_staff or request.user.is_superuser:
        years = YearAlbum.objects.all().order_by('-year')
    else:
        years = YearAlbum.objects.filter(status='approved').order_by('-year')

    # Группируем по 3 в ряд
    grouped_years = []
    for i in range(0, len(years), 3):
        grouped_years.append(years[i:i + 3])

    return render(request, 'media_archive/home.html', {'years': grouped_years})

# Поиск - только по одобренным учебным годам
def search_years(request):
    query = request.GET.get('q', '').strip()

    years = YearAlbum.objects.filter(status='approved')
    if query:
        years = years.filter(year__icontains=query)

    years = years.order_by('-year')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        results = []
        for year in years:
            results.append({
                'year': year.year,
                'id': year.id,
                'classes_count': year.classes.count(),
                'approved_classes_count': year.classes.filter(status='approved').count()
            })
        return JsonResponse({'results': results})

    grouped_years = []
    for i in range(0, len(years), 3):
        grouped_years.append(years[i:i + 3])

    return render(request, 'media_archive/home.html', {
        'years': grouped_years,
        'search_query': query
    })

# Просмотр учебного года - показываем одобренные классы
def year_detail(request, year_id):
    year = get_object_or_404(YearAlbum, id=year_id, status='approved')
    classes = year.classes.filter(status='approved').order_by('class_name')

    return render(request, 'media_archive/year_detail.html', {
        'year': year,
        'classes': classes
    })

# Просмотр событий в классе
def class_detail(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id, status='approved')
    events = school_class.events.filter(status='approved').order_by('-created_at')

    return render(request, 'media_archive/class_detail.html', {
        'school_class': school_class,
        'events': events
    })

# Просмотр события - показываем одобренные фото
def event_detail(request, event_id):
    event = get_object_or_404(EventAlbum, id=event_id, status='approved')
    photos = event.photos.filter(status='approved').order_by('-uploaded_at')

    return render(request, 'media_archive/event_detail.html', {
        'event': event,
        'photos': photos
    })

# Личный кабинет
@login_required
def profile(request):
    # Показываем ВСЕ годы, классы, события и фото пользователя, независимо от статуса
    user_years = YearAlbum.objects.filter(created_by=request.user)
    user_classes = SchoolClass.objects.filter(created_by=request.user)
    user_events = EventAlbum.objects.filter(created_by=request.user)
    user_photos = Photo.objects.filter(uploaded_by=request.user)

    # Данные для панели модератора
    pending_years_count = 0
    pending_classes_count = 0
    pending_events_count = 0
    pending_photos_count = 0

    if request.user.is_staff or request.user.is_superuser:
        pending_years_count = YearAlbum.objects.filter(status='pending').count()
        pending_classes_count = SchoolClass.objects.filter(status='pending').count()
        pending_events_count = EventAlbum.objects.filter(status='pending').count()
        pending_photos_count = Photo.objects.filter(status='pending').count()

    return render(request, 'media_archive/profile.html', {
        'user_years': user_years,
        'user_classes': user_classes,
        'user_events': user_events,
        'user_photos': user_photos,
        'pending_years_count': pending_years_count,
        'pending_classes_count': pending_classes_count,
        'pending_events_count': pending_events_count,
        'pending_photos_count': pending_photos_count,
    })

# Создание учебного года
@login_required
def create_year(request):
    if request.method == 'POST':
        form = YearAlbumForm(request.POST)
        if form.is_valid():
            year = form.save(commit=False)
            year.created_by = request.user

            # Авто-одобрение для админов и модераторов
            if request.user.is_staff or request.user.is_superuser:
                year.status = 'approved'
                messages.success(request, f'Учебный год {year.year} создан и опубликован!')
            else:
                year.status = 'pending'
                messages.success(request, f'Учебный год {year.year} создан и отправлен на модерацию!')

            year.save()

            # Редирект на предыдущую страницу или профиль
            next_url = request.POST.get('next', request.GET.get('next', 'profile'))
            return redirect(next_url)
    else:
        form = YearAlbumForm()

    return render(request, 'media_archive/create_year.html', {
        'form': form,
        'next': request.META.get('HTTP_REFERER', 'profile')
    })

# Создание класса
@login_required
def create_class(request):
    if request.method == 'POST':
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            school_class = form.save(commit=False)
            school_class.created_by = request.user

            if request.user.is_staff or request.user.is_superuser:
                school_class.status = 'approved'
                messages.success(request, f'Класс {school_class.class_name} создан и опубликован!')
            else:
                school_class.status = 'pending'
                messages.success(request, f'Класс {school_class.class_name} создан и отправлен на модерацию!')

            school_class.save()

            next_url = request.POST.get('next', request.GET.get('next', 'profile'))
            return redirect(next_url)
    else:
        form = SchoolClassForm()
        form.fields['year_album'].queryset = YearAlbum.objects.filter(status='approved')

    return render(request, 'media_archive/create_class.html', {
        'form': form,
        'next': request.META.get('HTTP_REFERER', 'profile')
    })

# Создание события
@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventAlbumForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user

            # Авто-одобрение для админов и модераторов
            if request.user.is_staff or request.user.is_superuser:
                event.status = 'approved'
                messages.success(request, f'Событие "{event.title}" создано и опубликовано!')
            else:
                event.status = 'pending'
                messages.success(request, f'Событие "{event.title}" создано и отправлено на модерацию!')

            event.save()

            next_url = request.POST.get('next', request.GET.get('next', 'profile'))
            return redirect(next_url)
    else:
        form = EventAlbumForm()
        form.fields['school_class'].queryset = SchoolClass.objects.filter(status='approved')

    return render(request, 'media_archive/create_event.html', {
        'form': form,
        'next': request.META.get('HTTP_REFERER', 'profile')
    })

# Загрузка фото
@login_required
def upload_photo(request):
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.uploaded_by = request.user

            # Авто-одобрение для админов и модераторов
            if request.user.is_staff or request.user.is_superuser:
                photo.status = 'approved'
                messages.success(request, 'Фото загружено и опубликовано!')
            else:
                photo.status = 'pending'
                messages.success(request, 'Фото загружено и отправлено на модерацию!')

            photo.save()

            # Для фото редиректим на событие, если оно известно
            next_url = request.POST.get('next', request.GET.get('next', 'profile'))
            if 'event_detail' in next_url:
                return redirect('event_detail', event_id=photo.event_album.id)
            return redirect(next_url)
    else:
        form = PhotoUploadForm()
        form.fields['event_album'].queryset = EventAlbum.objects.filter(status='approved')

    return render(request, 'media_archive/upload_photo.html', {
        'form': form,
        'next': request.META.get('HTTP_REFERER', 'profile')
    })

# Создание события для класса (с предвыбором)
@login_required
def create_event_for_class(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id, status='approved')

    if request.method == 'POST':
        form = EventAlbumForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.school_class = school_class

            if request.user.is_staff or request.user.is_superuser:
                event.status = 'approved'
                messages.success(request, f'Событие "{event.title}" создано и опубликовано!')
            else:
                event.status = 'pending'
                messages.success(request, f'Событие "{event.title}" создано и отправлено на модерацию!')

            event.save()
            return redirect('class_detail', class_id=class_id)
    else:
        form = EventAlbumForm(initial={'school_class': school_class})
        form.fields['school_class'].widget = forms.HiddenInput()

    return render(request, 'media_archive/create_event.html', {
        'form': form,
        'school_class': school_class,
        'predefined_class': True
    })

# Создание события для года (с предвыбором)
@login_required
def create_event_for_year(request, year_id):
    year = get_object_or_404(YearAlbum, id=year_id, status='approved')
    classes = year.classes.filter(status='approved')

    if request.method == 'POST':
        form = EventAlbumForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user

            if request.user.is_staff or request.user.is_superuser:
                event.status = 'approved'
                messages.success(request, f'Событие "{event.title}" создано и опубликовано!')
            else:
                event.status = 'pending'
                messages.success(request, f'Событие "{event.title}" создано и отправлено на модерацию!')

            event.save()
            return redirect('year_detail', year_id=year_id)
    else:
        form = EventAlbumForm()
        # Ограничиваем выбор только классами этого года
        form.fields['school_class'].queryset = classes

    return render(request, 'media_archive/create_event.html', {
        'form': form,
        'year': year,
        'predefined_year': True
    })

# Аутентификация
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Неверный логин или пароль')
    return render(request, 'media_archive/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not password1 or not password2:
            messages.error(request, 'Все поля должны быть заполнены.')
            return render(request, 'media_archive/register.html')

        if password1 != password2:
            messages.error(request, 'Пароли не совпадают.')
            return render(request, 'media_archive/register.html')

        from django.contrib.auth.models import User
        try:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Пользователь с таким именем уже существует.')
                return render(request, 'media_archive/register.html')

            user = User.objects.create_user(username=username, password=password1)
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Ошибка регистрации: {str(e)}')

    return render(request, 'media_archive/register.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('home')

# Модерация
@login_required
def moderation_dashboard(request):
    # Только для админов и модераторов
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для доступа к модерации')
        return redirect('home')

    pending_years = YearAlbum.objects.filter(status='pending')
    pending_classes = SchoolClass.objects.filter(status='pending')
    pending_events = EventAlbum.objects.filter(status='pending')
    pending_photos = Photo.objects.filter(status='pending')

    return render(request, 'media_archive/moderation_dashboard.html', {
        'pending_years': pending_years,
        'pending_classes': pending_classes,
        'pending_events': pending_events,
        'pending_photos': pending_photos,
    })

@login_required
def approve_year(request, year_id):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для модерации')
        return redirect('home')

    year = get_object_or_404(YearAlbum, id=year_id)
    year.status = 'approved'
    year.save()
    messages.success(request, f'Учебный год {year.year} одобрен!')
    return redirect('moderation_dashboard')

@login_required
def reject_year(request, year_id):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для модерации')
        return redirect('home')

    year = get_object_or_404(YearAlbum, id=year_id)
    year.status = 'rejected'
    year.save()
    messages.success(request, f'Учебный год {year.year} отклонен!')
    return redirect('moderation_dashboard')

@login_required
def approve_class(request, class_id):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для модерации')
        return redirect('home')

    school_class = get_object_or_404(SchoolClass, id=class_id)
    school_class.status = 'approved'
    school_class.save()
    messages.success(request, f'Класс {school_class.class_name} одобрен!')
    return redirect('moderation_dashboard')

@login_required
def reject_class(request, class_id):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для модерации')
        return redirect('home')

    school_class = get_object_or_404(SchoolClass, id=class_id)
    school_class.status = 'rejected'
    school_class.save()
    messages.success(request, f'Класс {school_class.class_name} отклонен!')
    return redirect('moderation_dashboard')

@login_required
def approve_event(request, event_id):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для модерации')
        return redirect('home')

    event = get_object_or_404(EventAlbum, id=event_id)
    event.status = 'approved'
    event.save()
    messages.success(request, f'Событие "{event.title}" одобрено!')
    return redirect('moderation_dashboard')

@login_required
def reject_event(request, event_id):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для модерации')
        return redirect('home')

    event = get_object_or_404(EventAlbum, id=event_id)
    event.status = 'rejected'
    event.save()
    messages.success(request, f'Событие "{event.title}" отклонено!')
    return redirect('moderation_dashboard')

@login_required
def approve_photo(request, photo_id):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для модерации')
        return redirect('home')

    photo = get_object_or_404(Photo, id=photo_id)
    photo.status = 'approved'
    photo.save()
    messages.success(request, 'Фото одобрено!')
    return redirect('moderation_dashboard')

@login_required
def reject_photo(request, photo_id):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для модерации')
        return redirect('home')

    photo = get_object_or_404(Photo, id=photo_id)
    photo.status = 'rejected'
    photo.save()
    messages.success(request, 'Фото отклонено!')
    return redirect('moderation_dashboard')

# Функция для отладки (можно удалить после тестирования)
def debug_home(request):
    years = YearAlbum.objects.filter(status='approved').order_by('-year')

    # Простой вывод без шаблона
    response = f"Найдено годов: {years.count()}<br><br>"
    for year in years:
        response += f"- {year.year} (ID: {year.id})<br>"

    return HttpResponse(response)
