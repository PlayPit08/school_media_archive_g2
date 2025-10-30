from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_years, name='search_years'),

    # Авторизация
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),

    # Просмотр контента
    path('year/<int:year_id>/', views.year_detail, name='year_detail'),
    path('class/<int:class_id>/', views.class_detail, name='class_detail'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),

    # Создание контента
    path('profile/create-year/', views.create_year, name='create_year'),
    path('profile/create-class/', views.create_class, name='create_class'),
    path('profile/create-event/', views.create_event, name='create_event'),
    path('profile/upload-photo/', views.upload_photo, name='upload_photo'),

    # Новые URL для создания событий с предвыбором
    path('year/<int:year_id>/create-event/', views.create_event_for_year, name='create_event_for_year'),
    path('class/<int:class_id>/create-event/', views.create_event_for_class, name='create_event_for_class'),

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

    # Отладка
    path('debug/', views.debug_home, name='debug_home'),
]
