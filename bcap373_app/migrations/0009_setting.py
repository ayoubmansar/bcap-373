# Generated by Django 4.0.3 on 2022-04-29 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bcap373_app', '0008_alter_eventmodel_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('send_email', models.BooleanField()),
            ],
        ),
    ]
