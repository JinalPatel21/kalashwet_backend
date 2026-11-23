from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0005_featuredproduct')]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image_file',
            field=models.ImageField(blank=True, null=True, upload_to='categories/'),
        ),
    ]
