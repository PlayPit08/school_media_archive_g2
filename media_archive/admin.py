from django.contrib import admin
from .models import YearAlbum, SchoolClass, EventAlbum, Photo

@admin.register(YearAlbum)
class YearAlbumAdmin(admin.ModelAdmin):
    list_display = ['year', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['year']
    list_editable = ['status']

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ['class_name', 'year_album', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'year_album', 'created_at']
    search_fields = ['class_name']
    list_editable = ['status']

@admin.register(EventAlbum)
class EventAlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'school_class', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'school_class', 'created_at']
    search_fields = ['title']
    list_editable = ['status']

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'event_album', 'status', 'uploaded_by', 'uploaded_at']
    list_filter = ['status', 'uploaded_at', 'event_album']
    search_fields = ['event_album__title']
    list_editable = ['status']
