from django import forms
from .models import YearAlbum, EventAlbum, Photo

class YearAlbumForm(forms.ModelForm):
    class Meta:
        model = YearAlbum
        fields = ['year']
        widgets = {
            'year': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: 2023-2024'
            })
        }
        labels = {
            'year': 'Учебный год'
        }

class EventAlbumForm(forms.ModelForm):
    class Meta:
        model = EventAlbum
        fields = ['title', 'year_album']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Выпускной вечер'
            }),
            'year_album': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'title': 'Название события',
            'year_album': 'Учебный год'
        }

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['event_album', 'image']
        widgets = {
            'event_album': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'event_album': 'Событие',
            'image': 'Фотография'
        }