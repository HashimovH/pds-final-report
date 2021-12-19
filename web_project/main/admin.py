from django.contrib import admin
from .models import Picture

# Register your models here.


class PictureAdmin(admin.ModelAdmin):
    list_display = ('picture', 'processed_image', 'created_at', 'updated_at',)
    list_per_page = 25


admin.site.register(Picture, PictureAdmin)
