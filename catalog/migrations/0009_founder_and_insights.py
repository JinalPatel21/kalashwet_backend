import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0008_jewelleryvideo_long_path')]

    operations = [
        migrations.CreateModel(
            name='FounderProfile',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(default='Dixit Vithani', max_length=120)),
                ('role', models.CharField(default='Founder', max_length=80)),
                ('quote', models.CharField(blank=True, default='', max_length=255)),
                ('story', models.TextField(blank=True, default='')),
                ('image', models.ImageField(max_length=255, upload_to='founder/')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'verbose_name': 'Founder profile', 'verbose_name_plural': 'Founder profile'},
        ),
        migrations.CreateModel(
            name='LatestInsight',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=160)),
                ('excerpt', models.CharField(blank=True, default='', max_length=300)),
                ('image', models.ImageField(max_length=255, upload_to='insights/')),
                ('link', models.CharField(blank=True, default='/jewellery', max_length=500)),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
            ],
            options={'ordering': ['sort_order', '-created_at']},
        ),
    ]
