from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "category", "unit", "location", "min_stock", "is_controlled", "is_active")
    search_fields = ("code", "name", "spec", "category", "location")
    list_filter = ("category", "is_controlled", "is_active")
