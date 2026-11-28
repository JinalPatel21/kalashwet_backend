from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('pricing', '0003_coupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metalrate',
            name='purity',
            field=models.CharField(
                choices=[
                    ('24K', '24K'),
                    ('22K', '22K'),
                    ('18K', '18K'),
                    ('14K', '14K'),
                    ('10K', '10K'),
                    ('9K', '9K'),
                    ('PT950', 'PT950'),
                    ('S925', 'S925'),
                ],
                max_length=10,
                unique=True,
            ),
        ),
    ]
