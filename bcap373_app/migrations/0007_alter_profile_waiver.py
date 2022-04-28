# Generated by Django 4.0.3 on 2022-04-28 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bcap373_app', '0006_alter_eventmodel_event_supervisor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='waiver',
            field=models.CharField(blank=True, help_text="If you have this user's waiver on file, please indicate this in this box (and give a link to where it can be found, e.g. on Google Drive)", max_length=300, null=True),
        ),
    ]