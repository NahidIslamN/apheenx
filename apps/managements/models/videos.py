from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator

User = settings.AUTH_USER_MODEL



class VideoMedia(models.Model):
    file = models.FileField(
        upload_to="videos/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['mp4', 'mov', 'avi', 'mkv', 'webm']
            )
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name



class Video(models.Model):
    CATEGORY_CHOICES = (
        ('entertainment', "Entertainment"),
        ('tutorial', "Tutorial"),
    )

    STATUS_CHOICES = (
        ('active', "Active"),
        ('inactive', "Inactive"),
        ('draft', "Draft"),
    )

    title = models.CharField(max_length=250, unique=True)
    description = models.TextField()

    price = models.DecimalField(max_digits=9, decimal_places=2)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='entertainment'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    # clearer naming
    trailers = models.ManyToManyField(
        VideoMedia,
        related_name='video_trailers',
        blank=True
    )

    videos = models.ManyToManyField(
        VideoMedia,
        related_name='video_contents',
        blank=True
    )

    thumbnail = models.ImageField(
        upload_to='thumbnails/'
    )

    subscribers = models.ManyToManyField(
        User,
        related_name='subscribers',
        blank=True
    )

    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.price}"



class VideoView(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="views")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_trailer = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)