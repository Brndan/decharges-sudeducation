# Generated by Django 3.2 on 2021-05-11 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('decharge', '0007_alter_tempsdedecharge_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utilisationcreditdetempssyndicalponctuel',
            name='demi_journees_de_decharges',
            field=models.PositiveIntegerField(default=0, verbose_name='Demi-journées de décharges utilisées'),
        ),
    ]