# Generated by Django 3.2.7 on 2021-10-10 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('round', '0002_alter_problem_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contestant',
            name='contestant_id',
            field=models.AutoField(editable=False, primary_key=True, serialize=False, verbose_name='Contestant ID'),
        ),
    ]
