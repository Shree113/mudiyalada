# Generated by Django 5.1.7 on 2025-03-20 01:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('option_a', models.CharField(max_length=255)),
                ('option_b', models.CharField(max_length=255)),
                ('option_c', models.CharField(max_length=255)),
                ('option_d', models.CharField(max_length=255)),
                ('correct_option', models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('department', models.CharField(max_length=100)),
                ('college', models.CharField(max_length=100)),
                ('year', models.CharField(max_length=20)),
                ('total_score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Leaderboard',
            fields=[
            ],
            options={
                'verbose_name': 'Leaderboard',
                'verbose_name_plural': 'Leaderboard',
                'ordering': ['-total_score'],
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('api.student',),
        ),
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chosen_option', models.CharField(max_length=1)),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.question')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.student')),
            ],
        ),
    ]
