# Generated by Django 4.2 on 2023-04-06 01:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("traits", "0003_remove_trait_pet"),
        ("pets", "0004_alter_pet_weight"),
    ]

    operations = [
        migrations.AddField(
            model_name="pet",
            name="traits",
            field=models.ManyToManyField(related_name="pets", to="traits.trait"),
        ),
        migrations.AlterField(
            model_name="pet",
            name="sex",
            field=models.CharField(
                choices=[
                    ("Male", "Male"),
                    ("Female", "Female"),
                    ("Not Informed", "Default"),
                ],
                default="Not Informed",
                max_length=20,
            ),
        ),
    ]
