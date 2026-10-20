
from django.contrib import admin
from .models import Space


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ("name", "creator", "topic", "created_at")
    search_fields = ("name", "description", "creator__username")
    list_filter = ("topic", "created_at")
    filter_horizontal = ("members",)
