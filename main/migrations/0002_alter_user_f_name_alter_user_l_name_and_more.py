# Generated by Django 5.1.4 on 2025-01-05 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='f_name',
            field=models.CharField(default='User', max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='l_name',
            field=models.CharField(default='User', max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='m_name',
            field=models.CharField(blank=True, default='User', max_length=50, null=True),
        ),
    ]
