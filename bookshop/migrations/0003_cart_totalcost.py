# Generated by Django 4.0.4 on 2022-05-03 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookshop', '0002_product_details_product_features_cart'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='totalcost',
            field=models.IntegerField(default=0),
        ),
    ]
