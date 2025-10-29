from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
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
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    
    # Создание контента
    path('profile/create-year/', views.create_year, name='create_year'),
    path('profile/create-event/', views.create_event, name='create_event'),
    path('profile/upload-photo/', views.upload_photo, name='upload_photo'),
    
    # Модерация
    path('moderation/', views.moderation_dashboard, name='moderation_dashboard'),
    path('moderation/year/<int:year_id>/approve/', views.approve_year, name='approve_year'),
    path('moderation/year/<int:year_id>/reject/', views.reject_year, name='reject_year'),
    path('moderation/event/<int:event_id>/approve/', views.approve_event, name='approve_event'),
    path('moderation/event/<int:event_id>/reject/', views.reject_event, name='reject_event'),
    path('moderation/photo/<int:photo_id>/approve/', views.approve_photo, name='approve_photo'),
    path('moderation/photo/<int:photo_id>/reject/', views.reject_photo, name='reject_photo'),
    
    # Отладка
    path('debug/', views.debug_home, name='debug_home'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)