from django.contrib import admin
from .models import UserProfile, FavoriteScan, Notification, Feedback, SystemLog

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'gender', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('role', 'gender', 'is_active')
    ordering = ('-created_at',)
    actions = ['toggle_active']

    def toggle_active(self, request, queryset):
        for profile in queryset:
            profile.is_active = not profile.is_active
            profile.save()
            profile.user.is_active = profile.is_active
            profile.user.save()
    toggle_active.short_description = "Toggle active status"

@admin.register(FavoriteScan)
class FavoriteScanAdmin(admin.ModelAdmin):
    list_display = ('user', 'prediction', 'created_at')
    search_fields = ('user__username', 'prediction__id')
    ordering = ('-created_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notif_type', 'is_read', 'created_at')
    search_fields = ('title', 'user__username', 'message')
    list_filter = ('notif_type', 'is_read')
    ordering = ('-created_at',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'category', 'rating', 'is_resolved', 'created_at')
    search_fields = ('subject', 'user__username', 'message')
    list_filter = ('category', 'is_resolved', 'rating')
    ordering = ('-created_at',)

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'ip_address', 'created_at')
    search_fields = ('action', 'user__username', 'description', 'ip_address')
    list_filter = ('action',)
    ordering = ('-created_at',)
