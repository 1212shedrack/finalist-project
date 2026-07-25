from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Prediction(models.Model):
    """Stores each disease detection result."""

    RISK_CHOICES = [
        ('Low',     'Low'),
        ('Medium',  'Medium'),
        ('High',    'High'),
        ('Unknown', 'Unknown'),
    ]

    # User who ran this scan (null = pre-auth legacy records, visible only to admins)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='predictions',
        verbose_name='Farmer',
    )

    image = models.ImageField(upload_to='predictions/')
    predicted_class = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100, default='Unknown')
    confidence = models.FloatField()
    all_probabilities = models.JSONField(default=dict)
    risk_level = models.CharField(max_length=20,
                                  choices=RISK_CHOICES,
                                  default='Unknown')
    risk_color = models.CharField(max_length=20, default='secondary')
    notes = models.TextField(blank=True)
    language_used = models.CharField(max_length=10, default='en',
                                     verbose_name='Language')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Prediction'
        verbose_name_plural = 'Predictions'

    def __str__(self):
        created = self.created_at.strftime("%Y-%m-%d %H:%M")
        user_str = self.user.username if self.user else 'Anonymous'
        return (
            f"{self.display_name} ({self.confidence:.1f}%)"
            f" — {user_str} — {created}"
        )

    @property
    def display_name_translated(self):
        mapping = {
            'health': _('Healthy'),
            'spot_leaf': _('Leaf Spot'),
            'white_rust': _('White Rust'),
            'non_amaranthus': _('Non-Amaranthus'),
            'Healthy': _('Healthy'),
            'Leaf Spot': _('Leaf Spot'),
            'White Rust': _('White Rust'),
            'Non-Amaranthus': _('Non-Amaranthus'),
        }
        return mapping.get(self.predicted_class, mapping.get(self.display_name, self.display_name))

    @property
    def risk_level_translated(self):
        mapping = {
            'Low': _('Low Risk'),
            'Medium': _('Medium Risk'),
            'High': _('High Risk'),
            'Unknown': _('Unknown'),
        }
        return mapping.get(self.risk_level, self.risk_level)

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


