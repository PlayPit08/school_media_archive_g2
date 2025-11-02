from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_years, name='search_years'),

    # Детальные страницы
    path('year/<int:year_id>/', views.year_detail, name='year_detail'),
    path('class/<int:class_id>/', views.class_detail, name='class_detail'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),

    # Аутентификация
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Личный кабинет и профиль
    path('profile/', views.profile, name='profile'),

    # Создание с предвыбором
    path('year/<int:year_id>/create-class/', views.create_class_for_year, name='create_class_for_year'),
    path('class/<int:class_id>/create-event/', views.create_event_for_class, name='create_event_for_class'),
    path('year/<int:year_id>/create-event/', views.create_event_for_year, name='create_event_for_year'),
    path('event/<int:event_id>/upload-photo/', views.upload_photo_for_event, name='upload_photo_for_event'),
    path('class/<int:class_id>/upload-photo/', views.upload_photo_for_class, name='upload_photo_for_class'),

    # Обычное создание (без предвыбора)
    path('create-year/', views.create_year, name='create_year'),
    path('create-class/', views.create_class, name='create_class'),
    path('create-event/', views.create_event, name='create_event'),
    path('upload-photo/', views.upload_photo, name='upload_photo'),

    # Модерация
    path('moderation/', views.moderation_dashboard, name='moderation_dashboard'),
    path('moderation/year/<int:year_id>/approve/', views.approve_year, name='approve_year'),
    path('moderation/year/<int:year_id>/reject/', views.reject_year, name='reject_year'),
    path('moderation/class/<int:class_id>/approve/', views.approve_class, name='approve_class'),
    path('moderation/class/<int:class_id>/reject/', views.reject_class, name='reject_class'),
    path('moderation/event/<int:event_id>/approve/', views.approve_event, name='approve_event'),
    path('moderation/event/<int:event_id>/reject/', views.reject_event, name='reject_event'),
    path('moderation/photo/<int:photo_id>/approve/', views.approve_photo, name='approve_photo'),
    path('moderation/photo/<int:photo_id>/reject/', views.reject_photo, name='reject_photo'),
    
    # Удаление
    path('year/<int:year_id>/delete/', views.delete_year, name='delete_year'),
    path('class/<int:class_id>/delete/', views.delete_class, name='delete_class'),
    path('event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('photo/<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),

    # Отладка
    path('debug/', views.debug_home, name='debug_home'),
]
