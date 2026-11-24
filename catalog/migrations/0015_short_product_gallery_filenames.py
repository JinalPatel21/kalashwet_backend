import catalog.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0014_navigation_feature')]

    operations = [
        migrations.AlterField(
            model_name='productmedia',
            name='image',
            field=models.ImageField(max_length=255, upload_to=catalog.models.product_gallery_upload_to),
        ),
    ]
