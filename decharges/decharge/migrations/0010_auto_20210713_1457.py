# Generated by Django 3.2 on 2021-07-13 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('decharge', '0009_alter_utilisationtempsdecharge_civilite'),
    ]

    operations = [
        migrations.AddField(
            model_name='utilisationtempsdecharge',
            name='date_debut_decharge',
            field=models.DateField(blank=True, null=True, verbose_name='Date à laquelle la décharge commence'),
        ),
        migrations.AddField(
            model_name='utilisationtempsdecharge',
            name='date_fin_decharge',
            field=models.DateField(blank=True, null=True, verbose_name='Date à laquelle la décharge se termine'),
        ),
    ]
