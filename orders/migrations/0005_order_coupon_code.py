from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('orders', '0004_order_source')]

    operations = [
        migrations.AddField(
            model_name='order',
            name='coupon_code',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
    ]
