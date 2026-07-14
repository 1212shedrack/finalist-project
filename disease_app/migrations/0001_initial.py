from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Prediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='predictions/')),
                ('predicted_class', models.CharField(max_length=100)),
                ('display_name', models.CharField(default='Unknown', max_length=100)),
                ('confidence', models.FloatField()),
                ('all_probabilities', models.JSONField(default=dict)),
                ('risk_level', models.CharField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'), ('Unknown', 'Unknown')], default='Unknown', max_length=20)),
                ('risk_color', models.CharField(default='secondary', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Prediction',
                'verbose_name_plural': 'Predictions',
                'ordering': ['-created_at'],
            },
        ),
    ]
