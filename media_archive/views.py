# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import YearAlbum, SchoolClass, EventAlbum, Photo
from .forms import YearAlbumForm, SchoolClassForm, EventAlbumForm, PhotoUploadForm

def home(request):
    years = YearAlbum.objects.filter(status='approved').order_by('-year')
    grouped_years = []
    for i in range(0, len(years), 3):
        grouped_years.append(years[i:i + 3])
    return render(request, 'media_archive/home.html', {'years': grouped_years})

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

def year_detail(request, year_id):
    year = get_object_or_404(YearAlbum, id=year_id, status='approved')
    classes = year.classes.filter(status='approved').order_by('created_at')
    classes_grouped = []
    for i in range(0, len(classes), 3):
        classes_grouped.append(classes[i:i + 3])
    return render(request, 'media_archive/year_detail.html', {
        'year': year,
        'classes': classes_grouped
    })

def class_detail(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id, status='approved')
    events = school_class.events.filter(status='approved').order_by('created_at')
    events_grouped = []
    for i in range(0, len(events), 3):
        events_grouped.append(events[i:i + 3])
    return render(request, 'media_archive/class_detail.html', {
        'school_class': school_class,
        'events': events_grouped
    })

def event_detail(request, event_id):
    event = get_object_or_404(EventAlbum, id=event_id, status='approved')
    photos = event.photos.filter(status='approved').order_by('uploaded_at')
    return render(request, 'media_archive/event_detail.html', {
        'event': event,
        'photos': photos
    })

@login_required
def profile(request):
    user_years = YearAlbum.objects.filter(created_by=request.user)
    user_classes = SchoolClass.objects.filter(created_by=request.user)
    user_events = EventAlbum.objects.filter(created_by=request.user)
    user_photos = Photo.objects.filter(uploaded_by=request.user).order_by('uploaded_at')
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

@login_required
def create_year(request):
    if request.method == 'POST':
        form = YearAlbumForm(request.POST)
        if form.is_valid():
            year = form.save(commit=False)
            year.created_by = request.user
            if request.user.is_staff or request.user.is_superuser:
                year.status = 'approved'
                messages.success(request, f'Учебный год {year.year} создан и опубликован!')
            else:
                year.status = 'pending'
                messages.success(request, f'Учебный год {year.year} создан и отправлен на модерацию!')
            year.save()
            next_url = request.POST.get('next', request.GET.get('next', 'profile'))
            return redirect(next_url)
    else:
        form = YearAlbumForm()
    return render(request, 'media_archive/create_year.html', {
        'form': form,
        'next': request.META.get('HTTP_REFERER', 'profile')
    })

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

@login_required
def create_event(request):
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
            next_url = request.POST.get('next', request.GET.get('next', 'profile'))
            return redirect(next_url)
    else:
        form = EventAlbumForm()
        form.fields['school_class'].queryset = SchoolClass.objects.filter(status='approved')
    return render(request, 'media_archive/create_event.html', {
        'form': form,
        'next': request.META.get('HTTP_REFERER', 'profile')
    })

@login_required
def upload_photo(request):
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            event_album = form.cleaned_data['event_album']
            images = request.FILES.getlist('images')
            if not images:
                messages.error(request, 'Пожалуйста, выберите хотя бы одну фотографию.')
                return render(request, 'media_archive/upload_photo.html', {'form': form})
            success_count = 0
            for image in images:
                photo = Photo(
                    event_album=event_album,
                    image=image,
                    uploaded_by=request.user
                )
                if request.user.is_staff or request.user.is_superuser:
                    photo.status = 'approved'
                else:
                    photo.status = 'pending'
                photo.save()
                success_count += 1
            if request.user.is_staff or request.user.is_superuser:
                messages.success(request, f'{success_count} фотографий загружено и опубликовано!')
            else:
                messages.success(request, f'{success_count} фотографий загружено и отправлено на модерацию!')
            next_url = request.POST.get('next', request.GET.get('next', 'profile'))
            if 'event_detail' in next_url:
                return redirect('event_detail', event_id=event_album.id)
            return redirect(next_url)
    else:
        form = PhotoUploadForm()
        form.fields['event_album'].queryset = EventAlbum.objects.filter(status='approved')
    return render(request, 'media_archive/upload_photo.html', {
        'form': form,
        'next': request.META.get('HTTP_REFERER', 'profile')
    })

@login_required
def create_class_for_year(request, year_id):
    year = get_object_or_404(YearAlbum, id=year_id, status='approved')
    if request.method == 'POST':
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            school_class = form.save(commit=False)
            school_class.created_by = request.user
            school_class.year_album = year
            if request.user.is_staff or request.user.is_superuser:
                school_class.status = 'approved'
                messages.success(request, f'Класс {school_class.class_name} создан и опубликован!')
            else:
                school_class.status = 'pending'
                messages.success(request, f'Класс {school_class.class_name} создан и отправлен на модерацию!')
            school_class.save()
            return redirect('year_detail', year_id=year_id)
    else:
        form = SchoolClassForm(initial={'year_album': year})
    form.fields['year_album'].widget = forms.HiddenInput()
    return render(request, 'media_archive/create_class.html', {
        'form': form,
        'year': year,
        'predefined_year': True
    })

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
        form.fields['school_class'].queryset = classes
    return render(request, 'media_archive/create_event.html', {
        'form': form,
        'year': year,
        'predefined_year': True
    })

@login_required
def upload_photo_for_event(request, event_id):
    event = get_object_or_404(EventAlbum, id=event_id, status='approved')
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('images')
            if not images:
                messages.error(request, 'Пожалуйста, выберите хотя бы одну фотографию.')
                return render(request, 'media_archive/upload_photo.html', {
                    'form': form,
                    'event': event,
                    'predefined_event': True
                })
            success_count = 0
            for image in images:
                photo = Photo(
                    event_album=event,
                    image=image,
                    uploaded_by=request.user
                )
                if request.user.is_staff or request.user.is_superuser:
                    photo.status = 'approved'
                else:
                    photo.status = 'pending'
                photo.save()
                success_count += 1
            if request.user.is_staff or request.user.is_superuser:
                messages.success(request, f'{success_count} фотографий загружено и опубликовано!')
            else:
                messages.success(request, f'{success_count} фотографий загружено и отправлено на модерацию!')
            return redirect('event_detail', event_id=event_id)
    else:
        form = PhotoUploadForm(initial={'event_album': event})
        form.fields['event_album'].widget = forms.HiddenInput()
    return render(request, 'media_archive/upload_photo.html', {
        'form': form,
        'event': event,
        'predefined_event': True
    })

@login_required
def upload_photo_for_class(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id, status='approved')
    events = school_class.events.filter(status='approved')
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            event_album = form.cleaned_data['event_album']
            images = request.FILES.getlist('images')
            if not images:
                messages.error(request, 'Пожалуйста, выберите хотя бы одну фотографию.')
                return render(request, 'media_archive/upload_photo.html', {
                    'form': form,
                    'school_class': school_class,
                    'predefined_class': True
                })
            success_count = 0
            for image in images:
                photo = Photo(
                    event_album=event_album,
                    image=image,
                    uploaded_by=request.user
                )
                if request.user.is_staff or request.user.is_superuser:
                    photo.status = 'approved'
                else:
                    photo.status = 'pending'
                photo.save()
                success_count += 1
            if request.user.is_staff or request.user.is_superuser:
                messages.success(request, f'{success_count} фотографий загружено и опубликовано!')
            else:
                messages.success(request, f'{success_count} фотографий загружено и отправлено на модерацию!')
            return redirect('class_detail', class_id=class_id)
    else:
        form = PhotoUploadForm()
        form.fields['event_album'].queryset = events
    return render(request, 'media_archive/upload_photo.html', {
        'form': form,
        'school_class': school_class,
        'predefined_class': True
    })

@login_required
def delete_year(request, year_id):
    year = get_object_or_404(YearAlbum, id=year_id)
    if year.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для удаления этого учебного года')
        return redirect('home')
    if request.method == 'POST':
        year_name = year.year
        year.delete()
        messages.success(request, f'Учебный год {year_name} удален!')
        return redirect('home')
    return render(request, 'media_archive/confirm_delete.html', {
        'object': year,
        'object_type': 'учебный год',
        'back_url': 'home'
    })

@login_required
def delete_class(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id)
    if school_class.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для удаления этого класса')
        return redirect('profile')
    if request.method == 'POST':
        class_name = school_class.class_name
        year_id = school_class.year_album.id
        school_class.delete()
        messages.success(request, f'Класс {class_name} удален!')
        return redirect('year_detail', year_id=year_id)
    return render(request, 'media_archive/confirm_delete.html', {
        'object': school_class,
        'object_type': 'класс',
        'back_url': 'year_detail',
        'back_id': school_class.year_album.id
    })

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(EventAlbum, id=event_id)
    if event.created_by != request.user and not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для удаления этого события')
        return redirect('profile')
    if request.method == 'POST':
        event_title = event.title
        class_id = event.school_class.id
        event.delete()
        messages.success(request, f'Событие "{event_title}" удалено!')
        return redirect('class_detail', class_id=class_id)
    return render(request, 'media_archive/confirm_delete.html', {
        'object': event,
        'object_type': 'событие',
        'back_url': 'class_detail',
        'back_id': event.school_class.id
    })

@login_required
def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    if photo.uploaded_by != request.user and not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для удаления этой фотографии')
        return redirect('profile')
    if request.method == 'POST':
        event_id = photo.event_album.id
        photo.delete()
        messages.success(request, 'Фотография удалена!')
        return redirect('event_detail', event_id=event_id)
    return render(request, 'media_archive/confirm_delete.html', {
        'object': photo,
        'object_type': 'фотографию',
        'back_url': 'event_detail',
        'back_id': photo.event_album.id
    })

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

@login_required
def moderation_dashboard(request):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для доступа к модерации')
        return redirect('home')
    pending_years = YearAlbum.objects.filter(status='pending')
    pending_classes = SchoolClass.objects.filter(status='pending')
    pending_events = EventAlbum.objects.filter(status='pending')
    pending_photos = Photo.objects.filter(status='pending').order_by('uploaded_at')
    return render(request, 'media_archive/moderation_dashboard.html', {
        'pending_years': pending_years,
        'pending_classes': pending_classes,
        'pending_events': pending_events,
        'pending_photos': pending_photos,
    })

@login_required
def confirm_moderation(request, action, object_type, object_id):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для модерации')
        return redirect('home')
    type_names = {
        'year': 'учебный год',
        'class': 'класс', 
        'event': 'событие',
        'photo': 'фотографию'
    }
    if object_type == 'year':
        obj = get_object_or_404(YearAlbum, id=object_id)
        object_name = obj.year
        object_details = {
            'created_by': obj.created_by.username,
            'created_at': obj.created_at.strftime("%d.%m.%Y"),
        }
    elif object_type == 'class':
        obj = get_object_or_404(SchoolClass, id=object_id)
        object_name = obj.class_name
        object_details = {
            'year': obj.year_album.year,
            'created_by': obj.created_by.username,
            'created_at': obj.created_at.strftime("%d.%m.%Y"),
        }
    elif object_type == 'event':
        obj = get_object_or_404(EventAlbum, id=object_id)
        object_name = obj.title
        object_details = {
            'class_name': obj.school_class.class_name,
            'created_by': obj.created_by.username,
            'created_at': obj.created_at.strftime("%d.%m.%Y"),
        }
    elif object_type == 'photo':
        obj = get_object_or_404(Photo, id=object_id)
        object_name = f"Фото #{obj.id}"
        object_details = {
            'event_title': obj.event_album.title,
            'uploaded_by': obj.uploaded_by.username,
            'uploaded_at': obj.uploaded_at.strftime("%d.%m.%Y"),
            'image_url': obj.image.url if obj.image else None,
        }
    else:
        return redirect('moderation_dashboard')
    context = {
        'action': action,
        'object_type': type_names[object_type],
        'object_type_eng': object_type,
        'object_id': object_id,
        'object_name': object_name,
        'object_details': object_details,
    }
    return render(request, 'media_archive/confirm_moderation.html', context)

@login_required
def process_moderation(request):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для модерации')
        return redirect('home')
    if request.method != 'POST':
        return redirect('moderation_dashboard')
    object_type = request.POST.get('object_type')
    object_id = request.POST.get('object_id')
    action = request.POST.get('action')
    if not object_type or not object_id or not action:
        messages.error(request, 'Неверные параметры запроса')
        return redirect('moderation_dashboard')
    try:
        object_id = int(object_id)
    except (ValueError, TypeError):
        messages.error(request, 'Неверный ID объекта')
        return redirect('moderation_dashboard')
    if object_type == 'year':
        obj = get_object_or_404(YearAlbum, id=object_id)
        obj.status = 'approved' if action == 'approve' else 'rejected'
        obj.save()
        action_text = 'одобрен' if action == 'approve' else 'отклонен'
        messages.success(request, f'Учебный год "{obj.year}" {action_text}!')
    elif object_type == 'class':
        obj = get_object_or_404(SchoolClass, id=object_id)
        obj.status = 'approved' if action == 'approve' else 'rejected'
        obj.save()
        action_text = 'одобрен' if action == 'approve' else 'отклонен'
        messages.success(request, f'Класс "{obj.class_name}" {action_text}!')
    elif object_type == 'event':
        obj = get_object_or_404(EventAlbum, id=object_id)
        obj.status = 'approved' if action == 'approve' else 'rejected'
        obj.save()
        action_text = 'одобрено' if action == 'approve' else 'отклонено'
        messages.success(request, f'Событие "{obj.title}" {action_text}!')
    elif object_type == 'photo':
        obj = get_object_or_404(Photo, id=object_id)
        obj.status = 'approved' if action == 'approve' else 'rejected'
        obj.save()
        action_text = 'одобрено' if action == 'approve' else 'отклонено'
        messages.success(request, f'Фото #{obj.id} {action_text}!')
    else:
        messages.error(request, 'Неизвестный тип объекта')
        return redirect('moderation_dashboard')
    return redirect('moderation_dashboard')

def debug_home(request):
    years = YearAlbum.objects.filter(status='approved').order_by('-year')
    response = f"Найдено годов: {years.count()}<br><br>"
    for year in years:
        response += f"- {year.year} (ID: {year.id})<br>"
    return HttpResponse(response)