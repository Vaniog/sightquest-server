# Generated by Django 4.0.1 on 2024-02-20 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailer', '0005_rename_email_mailing_from_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailing',
            name='status',
            field=models.CharField(choices=[('SUCCEEDED', 'Succeeded'), ('FAILED', 'Failed')], default='FAILED', max_length=10),
        ),
    ]
