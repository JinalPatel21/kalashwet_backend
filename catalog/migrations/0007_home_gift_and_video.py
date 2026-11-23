import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0006_category_image_file')]

    operations = [
        migrations.CreateModel(
            name='GiftGuide',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=80)),
                ('image', models.ImageField(upload_to='gift-guides/')),
                ('cta', models.CharField(default='Shop now', max_length=60)),
                ('link', models.CharField(default='/jewellery', max_length=500)),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
            ],
            options={'ordering': ['sort_order', 'title']},
        ),
        migrations.CreateModel(
            name='JewelleryVideo',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=120)),
                ('video', models.FileField(upload_to='jewellery-videos/')),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='jewellery-video-thumbnails/')),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
            ],
            options={'ordering': ['sort_order', 'title'], 'verbose_name': 'Jewellery video', 'verbose_name_plural': 'Jewellery videos'},
        ),
    ]
