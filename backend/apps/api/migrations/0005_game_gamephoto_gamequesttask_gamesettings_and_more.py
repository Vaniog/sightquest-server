# Generated by Django 4.0.1 on 2024-01-31 12:29

import apps.api.models
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0005_remove_customuser_hosted_lobby'),
        ('api', '0004_remove_playerlobby_host'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('ended_at', models.DateTimeField(null=True)),
                ('host', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_games', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GamePhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=apps.api.models.game_image_file_path)),
                ('upload_time', models.DateTimeField(auto_now_add=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='api.game')),
            ],
        ),
        migrations.CreateModel(
            name='GameQuestTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='game_tasks', to='api.game')),
            ],
        ),
        migrations.CreateModel(
            name='GameSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(max_length=50)),
                ('duration', models.DurationField(default=datetime.timedelta(seconds=3600))),
            ],
        ),
        migrations.CreateModel(
            name='PlayerTaskCompletion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed_at', models.DateTimeField()),
                ('game_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_completions', to='api.gamequesttask')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_completions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GameUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='playerlobby',
            name='players',
        ),
        migrations.RemoveField(
            model_name='playerlobby',
            name='questpoints',
        ),
        migrations.RemoveField(
            model_name='playerlobbymembership',
            name='lobby',
        ),
        migrations.RemoveField(
            model_name='playerlobbymembership',
            name='player',
        ),
        migrations.RemoveField(
            model_name='questcompleted',
            name='lobby',
        ),
        migrations.RemoveField(
            model_name='questcompleted',
            name='task',
        ),
        migrations.RemoveField(
            model_name='questcompleted',
            name='user',
        ),
        migrations.RemoveField(
            model_name='questpoint',
            name='tasks',
        ),
        migrations.AddField(
            model_name='questtask',
            name='quest_point',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='api.questpoint'),
        ),
        migrations.AlterField(
            model_name='questpoint',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.coordinate'),
        ),
        migrations.DeleteModel(
            name='LobbyPhoto',
        ),
        migrations.DeleteModel(
            name='PlayerLobby',
        ),
        migrations.DeleteModel(
            name='PlayerLobbyMembership',
        ),
        migrations.DeleteModel(
            name='QuestCompleted',
        ),
        migrations.AddField(
            model_name='gamequesttask',
            name='quest_task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.questtask'),
        ),
        migrations.AddField(
            model_name='game',
            name='players',
            field=models.ManyToManyField(related_name='games', through='api.GameUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='game',
            name='settings',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='game', to='api.gamesettings'),
        ),
    ]
