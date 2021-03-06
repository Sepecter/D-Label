# Generated by Django 4.0.3 on 2022-03-13 06:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Collection_Info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(default='Untitled', max_length=1024)),
                ('photo_number', models.IntegerField(default='0')),
                ('class_number', models.IntegerField(default='0')),
            ],
        ),
        migrations.CreateModel(
            name='Label_Info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label_name', models.TextField(default='', max_length=32)),
                ('number', models.IntegerField(default=0)),
                ('belonging', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server.collection_info')),
            ],
        ),
        migrations.CreateModel(
            name='User_Info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.TextField(default='')),
                ('password', models.TextField(default='', max_length=32)),
                ('token', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='Photo_Info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.BinaryField()),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server.collection_info')),
                ('label', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server.label_info')),
            ],
        ),
        migrations.AddField(
            model_name='collection_info',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server.user_info'),
        ),
    ]
