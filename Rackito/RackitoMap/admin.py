from django.contrib import admin
from .models import Point, Tag, EmailVerification

# Register your models here.

@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ('id', 'latitude', 'longitude', 'point_type', 'address', 'popup_text')
    list_filter = ('point_type', 'tags')
    search_fields = ('popup_text', 'address', 'tags__name')
    filter_horizontal = ('tags',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')
    search_fields = ('user__username', 'user__email')
