# Generated by Django 4.1.2 on 2023-02-27 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_alter_postjobmodel_deadline'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username1',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
