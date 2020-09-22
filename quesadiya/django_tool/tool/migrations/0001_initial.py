# Generated by Django 3.1.1 on 2020-09-10 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectInfoModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=50)),
                ('participants', models.TextField()),
                ('description', models.TextField()),
                ('total', models.IntegerField()),
                ('finish', models.IntegerField()),
                ('unLabled', models.IntegerField()),
                ('abolished', models.IntegerField()),
            ],
        ),
    ]