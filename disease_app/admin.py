import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import Prediction


def export_csv(modeladmin, request, queryset):
    """Export selected predictions to CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="predictions.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Predicted Class', 'Display Name', 'Confidence (%)', 'Risk Level', 'Date'])
    for p in queryset:
        writer.writerow([p.id, p.predicted_class, p.display_name,
                         f'{p.confidence:.2f}', p.risk_level, p.created_at.strftime('%Y-%m-%d %H:%M')])
    return response

export_csv.short_description = 'Export selected to CSV'


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display    = ['id', 'image_preview', 'display_name', 'confidence_display', 'risk_badge', 'created_at']
    list_filter     = ['predicted_class', 'risk_level', 'created_at']
    search_fields   = ['predicted_class', 'display_name', 'notes']
    readonly_fields = ['image_preview', 'created_at', 'all_probabilities']
    ordering        = ['-created_at']
    actions         = [export_csv]
    list_per_page   = 25

    fieldsets = (
        ('Prediction Result', {
            'fields': ('image', 'image_preview', 'predicted_class', 'display_name', 'confidence', 'risk_level', 'risk_color')
        }),
        ('Probabilities', {
            'fields': ('all_probabilities',),
            'classes': ('collapse',),
        }),
        ('Meta', {
            'fields': ('notes', 'created_at'),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:8px;" />',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Preview'

    def confidence_display(self, obj):
        return format_html('<strong>{:.1f}%</strong>', obj.confidence)
    confidence_display.short_description = 'Confidence'

    def risk_badge(self, obj):
        colors = {'Low': '#28a745', 'Medium': '#fd7e14', 'High': '#dc3545', 'Unknown': '#6c757d'}
        color  = colors.get(obj.risk_level, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;">{}</span>',
            color, obj.risk_level
        )
    risk_badge.short_description = 'Risk'


# Customize admin site appearance
admin.site.site_header  = 'Amaranthus Disease Detection — Admin'
admin.site.site_title   = 'Amaranthus Admin'
admin.site.index_title  = 'System Administration'
