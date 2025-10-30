from django import forms
from .models import YearAlbum, SchoolClass, EventAlbum, Photo

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

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'event_album']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'event_album': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только одобренные события
        self.fields['event_album'].queryset = EventAlbum.objects.filter(status='approved')
