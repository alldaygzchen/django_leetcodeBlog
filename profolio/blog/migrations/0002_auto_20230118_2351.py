# Generated by Django 3.1.5 on 2023-01-18 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image_name',
            field=models.ImageField(upload_to='posts'),
        ),
    ]