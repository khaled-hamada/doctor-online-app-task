# Generated by Django 3.2.6 on 2021-08-23 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_user_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(blank=True, choices=[('patient', 'Patient'), ('doctor', 'Doctor')], max_length=64, null=True),
        ),
    ]
