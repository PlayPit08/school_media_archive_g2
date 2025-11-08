from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import YearAlbum, SchoolClass, EventAlbum, Photo

# Убираем группы
admin.site.unregister(Group)

# Кастомная форма для изменения пользователя (убираем ненужные поля)
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'password', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем ненужные поля из формы
        if 'email' in self.fields:
            del self.fields['email']
        if 'first_name' in self.fields:
            del self.fields['first_name']
        if 'last_name' in self.fields:
            del self.fields['last_name']

# Кастомная форма для создания пользователя
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем ненужные поля из формы
        if 'email' in self.fields:
            del self.fields['email']
        if 'first_name' in self.fields:
            del self.fields['first_name']
        if 'last_name' in self.fields:
            del self.fields['last_name']

# Кастомная админка для стандартного пользователя
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # Переопределяем fieldsets чтобы убрать ненужные поля
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    
    # В списке отображаем только нужные поля
    list_display = ('username', 'is_staff', 'is_superuser')
    search_fields = ('username',)

# Перерегистрируем стандартного пользователя с нашей кастомной админкой
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Ваши модели
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