from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from .models import YearAlbum, SchoolClass, EventAlbum, Photo
import re

class YearAlbumForm(forms.ModelForm):
    class Meta:
        model = YearAlbum
        fields = ['year']
        widgets = {
            'year': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: 2023-2024'
            }),
        }

    def clean_year(self):
        year = self.cleaned_data.get('year')

        # Проверка формата "год-год"
        pattern = r'^\d{4}-\d{4}$'
        if not re.match(pattern, year):
            raise forms.ValidationError('Формат года должен быть: год-год (например: 2023-2024)')

        # Разделяем годы
        try:
            start_year, end_year = map(int, year.split('-'))
        except ValueError:
            raise forms.ValidationError('Неверный формат года')

        # Проверяем минимальный год
        if start_year < 1950:
            raise forms.ValidationError('Минимальный год: 1950')

        # Проверяем что второй год на 1 больше первого
        if end_year != start_year + 1:
            raise forms.ValidationError('Второй год должен быть на 1 больше первого (например: 2023-2024)')

        return year

class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['class_name', 'year_album']
        widgets = {
            'class_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: 5А'
            }),
            'year_album': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только одобренные учебные годы
        self.fields['year_album'].queryset = YearAlbum.objects.filter(status='approved')

    def clean_class_name(self):
        class_name = self.cleaned_data.get('class_name')

        # Удаляем пробелы и приводим к верхнему регистру
        class_name = class_name.strip().upper()

        # Проверяем формат: цифра от 1 до 11 + буква (опционально)
        pattern = r'^(1[0-1]|[1-9])([А-ЯЁA-Z])?$'
        if not re.match(pattern, class_name):
            raise forms.ValidationError('Формат класса: цифра от 1 до 11 и буква (например: 5А, 10Б)')

        # Извлекаем цифровую часть
        class_number = int(re.findall(r'\d+', class_name)[0])

        # Проверяем что номер класса от 1 до 11
        if class_number < 1 or class_number > 11:
            raise forms.ValidationError('Номер класса должен быть от 1 до 11')

        return class_name

class EventAlbumForm(forms.ModelForm):
    class Meta:
        model = EventAlbum
        fields = ['title', 'school_class']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Первый звонок'
            }),
            'school_class': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только одобренные классы
        self.fields['school_class'].queryset = SchoolClass.objects.filter(status='approved')

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class PhotoUploadForm(forms.ModelForm):
    # Используем кастомное поле для множественной загрузки
    images = MultipleImageField(
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'multiple': True,
            'accept': 'image/*'
        }),
        label='Выберите фотографии',
        required=False
    )
    
    class Meta:
        model = Photo
        fields = ['event_album']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event_album'].queryset = EventAlbum.objects.filter(status='approved')
