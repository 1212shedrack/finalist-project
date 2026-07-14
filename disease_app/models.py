from django.db import models


class Prediction(models.Model):
    """Stores each disease detection result."""

    RISK_CHOICES = [
        ('Low',     'Low'),
        ('Medium',  'Medium'),
        ('High',    'High'),
        ('Unknown', 'Unknown'),
    ]

    image          = models.ImageField(upload_to='predictions/')
    predicted_class = models.CharField(max_length=100)
    display_name   = models.CharField(max_length=100, default='Unknown')
    confidence     = models.FloatField()
    all_probabilities = models.JSONField(default=dict)
    risk_level     = models.CharField(max_length=20, choices=RISK_CHOICES, default='Unknown')
    risk_color     = models.CharField(max_length=20, default='secondary')
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Prediction'
        verbose_name_plural = 'Predictions'

    def __str__(self):
        return f'{self.display_name} ({self.confidence:.1f}%) — {self.created_at.strftime("%Y-%m-%d %H:%M")}'

    def get_risk_badge_class(self):
        """Return Bootstrap badge class for the risk level."""
        mapping = {
            'Low':     'success',
            'Medium':  'warning',
            'High':    'danger',
            'Unknown': 'secondary',
        }
        return mapping.get(self.risk_level, 'secondary')

    def confidence_percentage(self):
        return round(self.confidence, 1)
