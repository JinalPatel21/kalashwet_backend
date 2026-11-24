import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0012_instagram_gallery')]

    operations = [
        migrations.CreateModel(
            name='StoreFAQ',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question', models.CharField(max_length=240)),
                ('answer', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
            ],
            options={'ordering': ['sort_order', 'id'], 'verbose_name': 'Store FAQ', 'verbose_name_plural': 'Store FAQs'},
        ),
    ]
