import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='HomeBanner',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=160)),
                ('subtitle', models.CharField(blank=True, default='', max_length=300)),
                ('cta', models.CharField(blank=True, default='Shop now', max_length=60)),
                ('link', models.CharField(blank=True, default='/jewellery', max_length=500)),
                ('image', models.ImageField(upload_to='banners/')),
                ('show_on_home', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
            ],
            options={'ordering': ['sort_order', '-created_at'], 'verbose_name': 'Home banner', 'verbose_name_plural': 'Home banners'},
        ),
    ]
