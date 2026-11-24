import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0011_brand_difference')]

    operations = [
        migrations.CreateModel(
            name='InstagramProfile',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('handle', models.CharField(default='@kalashwet', max_length=100)),
                ('profile_url', models.URLField(blank=True, default='', max_length=300)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'verbose_name': 'Instagram profile', 'verbose_name_plural': 'Instagram profile'},
        ),
        migrations.CreateModel(
            name='InstagramPost',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(max_length=255, upload_to='instagram/')),
                ('alt_text', models.CharField(blank=True, default='', max_length=160)),
                ('post_url', models.URLField(blank=True, default='', max_length=300)),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
            ],
            options={'ordering': ['sort_order', '-created_at']},
        ),
    ]
