# Generated by Django 3.2.9 on 2021-12-01 21:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_software_default_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='software',
            name='tool',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='core.tool'),
        ),
    ]