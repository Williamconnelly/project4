# Generated by Django 2.0.7 on 2018-08-07 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0004_auto_20180807_2134'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]