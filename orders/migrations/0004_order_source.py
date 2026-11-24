from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_status_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='source',
            field=models.CharField(choices=[('online_store', 'Online store'), ('draft_order', 'Draft order')], default='online_store', max_length=20),
        ),
    ]
