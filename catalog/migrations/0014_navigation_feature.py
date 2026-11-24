import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0013_store_faq')]

    operations = [
        migrations.CreateModel(
            name='NavigationFeature',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('eyebrow', models.CharField(default='The Kalashwet edit', max_length=80)),
                ('title', models.CharField(default='Made to be treasured', max_length=120)),
                ('cta', models.CharField(default='Discover more', max_length=60)),
                ('link', models.CharField(default='/jewellery', max_length=500)),
                ('image', models.ImageField(max_length=255, upload_to='navigation/')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'verbose_name': 'Navigation feature', 'verbose_name_plural': 'Navigation feature'},
        ),
    ]
