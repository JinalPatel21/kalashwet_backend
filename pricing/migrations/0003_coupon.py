import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('pricing', '0002_storeshippingsettings')]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(max_length=30, unique=True)),
                ('discount_type', models.CharField(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed amount')], default='percentage', max_length=12)),
                ('value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('minimum_order', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('maximum_discount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ['code']},
        ),
    ]
