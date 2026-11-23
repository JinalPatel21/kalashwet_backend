from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0007_home_gift_and_video')]

    operations = [
        migrations.AlterField(
            model_name='jewelleryvideo',
            name='video',
            field=models.FileField(max_length=255, upload_to='jewellery-videos/'),
        ),
    ]
