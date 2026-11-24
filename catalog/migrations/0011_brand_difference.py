import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0010_product_detail_gallery')]

    operations = [
        migrations.CreateModel(
            name='BrandDifference',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=140)),
                ('subtitle', models.CharField(blank=True, default='', max_length=240)),
                ('image', models.ImageField(max_length=255, upload_to='brand-differences/')),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
            ],
            options={'ordering': ['sort_order', 'title']},
        ),
    ]
