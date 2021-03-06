# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-30 09:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('jmbo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DummyModel',
            fields=[
                ('modelbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jmbo.ModelBase')),
                ('test_editable_field', models.CharField(max_length=32)),
                ('test_non_editable_field', models.CharField(editable=False, max_length=32)),
            ],
            options={
                'abstract': False,
            },
            bases=('jmbo.modelbase',),
        ),
        migrations.CreateModel(
            name='DummyRelationalModel1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='DummyRelationalModel2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='DummySourceModelBase',
            fields=[
                ('modelbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jmbo.ModelBase')),
                ('points_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.DummyModel')),
                ('points_to_many', models.ManyToManyField(related_name='to_many', to='tests.DummyModel')),
            ],
            options={
                'abstract': False,
            },
            bases=('jmbo.modelbase',),
        ),
        migrations.CreateModel(
            name='DummyTargetModelBase',
            fields=[
                ('modelbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jmbo.ModelBase')),
            ],
            options={
                'abstract': False,
            },
            bases=('jmbo.modelbase',),
        ),
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('modelbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jmbo.ModelBase')),
                ('content', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('jmbo.modelbase',),
        ),
        migrations.CreateModel(
            name='TrunkModel',
            fields=[
                ('modelbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jmbo.ModelBase')),
            ],
            options={
                'abstract': False,
            },
            bases=('jmbo.modelbase',),
        ),
        migrations.CreateModel(
            name='BranchModel',
            fields=[
                ('trunkmodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tests.TrunkModel')),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.trunkmodel',),
        ),
        migrations.AddField(
            model_name='dummymodel',
            name='test_foreign_field',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tests.DummyRelationalModel1'),
        ),
        migrations.AddField(
            model_name='dummymodel',
            name='test_foreign_published',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='foreign_published', to='tests.DummyTargetModelBase'),
        ),
        migrations.AddField(
            model_name='dummymodel',
            name='test_foreign_unpublished',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='foreign_unpublished', to='tests.DummyTargetModelBase'),
        ),
        migrations.AddField(
            model_name='dummymodel',
            name='test_many_field',
            field=models.ManyToManyField(to='tests.DummyRelationalModel2'),
        ),
        migrations.AddField(
            model_name='dummymodel',
            name='test_many_published',
            field=models.ManyToManyField(blank=True, null=True, related_name='many_published', to='tests.DummyTargetModelBase'),
        ),
        migrations.AddField(
            model_name='dummymodel',
            name='test_many_unpublished',
            field=models.ManyToManyField(blank=True, null=True, related_name='many_unpublished', to='tests.DummyTargetModelBase'),
        ),
        migrations.CreateModel(
            name='LeafModel',
            fields=[
                ('branchmodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tests.BranchModel')),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.branchmodel',),
        ),
    ]
