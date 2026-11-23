import django.db.models.deletion
import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0009_founder_and_insights')]

    operations = [
        migrations.AddField('product', 'height_mm', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
        migrations.AddField('product', 'width_mm', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
        migrations.AddField('product', 'depth_mm', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
        migrations.AddField('product', 'package_contents', models.CharField(blank=True, default='', max_length=255)),
        migrations.CreateModel(
            name='ProductMedia',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(max_length=255, upload_to='products/gallery/')),
                ('kind', models.CharField(choices=[('product', 'Product image'), ('lifestyle', 'Lifestyle image'), ('dimensions', 'Dimensions image'), ('packaging', 'Packaging image')], default='product', max_length=20)),
                ('alt_text', models.CharField(blank=True, default='', max_length=160)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery', to='catalog.product')),
            ],
            options={'ordering': ['sort_order', 'created_at'], 'verbose_name': 'Product gallery image', 'verbose_name_plural': 'Product gallery images'},
        ),
    ]
