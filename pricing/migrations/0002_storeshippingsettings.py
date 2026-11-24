import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('pricing', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='StoreShippingSettings',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('key', models.CharField(default='default', max_length=20, unique=True)),
                ('shipping_fee', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
            options={
                'verbose_name': 'Store shipping settings',
                'verbose_name_plural': 'Store shipping settings',
            },
        ),
    ]
