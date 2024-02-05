from django.contrib import admin
from .models import Subscriber


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'email', 'telegram', 'approved')
    list_filter = ('approved',)
    search_fields = ('email', 'telegram')
    list_editable = ('approved',)
