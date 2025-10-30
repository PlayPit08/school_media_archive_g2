from django.db import models
from django.contrib.auth.models import User

class YearAlbum(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На модерации'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    year = models.CharField(max_length=9, verbose_name='Учебный год')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Создатель'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Учебный год'
        verbose_name_plural = 'Учебные годы'
        ordering = ['-year']

    def __str__(self):
        return self.year

class SchoolClass(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На модерации'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    class_name = models.CharField(max_length=50, verbose_name='Название класса')
    year_album = models.ForeignKey(
        YearAlbum,
        on_delete=models.CASCADE,
        related_name='classes',
        verbose_name='Учебный год'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Создатель'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Класс'
        verbose_name_plural = 'Классы'
        ordering = ['class_name']

    def __str__(self):
        return f"{self.class_name} ({self.year_album.year})"

    @property
    def approved_events_count(self):
        """Количество одобренных событий в классе"""
        return self.events.filter(status='approved').count()

class EventAlbum(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На модерации'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name='Название события'
    )
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Класс'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Создатель'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def approved_photos_count(self):
        """Количество одобренных фотографий в событии"""
        return self.photos.filter(status='approved').count()

class Photo(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На модерации'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    event_album = models.ForeignKey(
        EventAlbum,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Событие'
    )
    image = models.ImageField(
        upload_to='photos/',
        verbose_name='Фотография'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Загрузил'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки'
    )

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Фото {self.id} - {self.event_album.title}"
