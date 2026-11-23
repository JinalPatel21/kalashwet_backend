from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0002_homebanner')]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='image_file',
            field=models.ImageField(blank=True, null=True, upload_to='collections/'),
        ),
    ]
