# Generated by Django 5.0.2 on 2024-02-26 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customer_id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=15)),
                ('age', models.IntegerField()),
                ('monthly_salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('approved_limit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('current_debt', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
    ]
