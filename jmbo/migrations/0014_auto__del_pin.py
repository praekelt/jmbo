# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from jmbo import USE_GIS


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Pin'
        db.delete_table(u'jmbo_pin')

    def backwards(self, orm):
        # Adding model 'Pin'
        db.create_table(u'jmbo_pin', (
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['category.Category'])),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jmbo.ModelBase'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('jmbo', ['Pin'])

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'category.category': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['category.Category']", 'null': 'True', 'blank': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sites.Site']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'category.tag': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Tag'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['category.Category']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'jmbo.modelbase': {
            'Meta': {'ordering': "('-publish_on', '-created')", 'object_name': 'ModelBase'},
            'anonymous_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'anonymous_likes': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['category.Category']", 'null': 'True', 'blank': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'comment_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'comments_closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comments_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'blank': 'True'}),
            'crop_from': ('django.db.models.fields.CharField', [], {'default': "'center'", 'max_length': '10', 'blank': 'True'}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'effect': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'modelbase_related'", 'null': 'True', 'to': u"orm['photologue.PhotoEffect']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_attribution': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'likes_closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'likes_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'owner_override': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'primary_category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'primary_modelbase_set'", 'null': 'True', 'to': u"orm['category.Category']"}),
            'publish_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'publishers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['publisher.Publisher']", 'null': 'True', 'blank': 'True'}),
            'retract_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sites.Site']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'unpublished'", 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['category.Tag']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'view_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'vote_total': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'jmbo.relation': {
            'Meta': {'unique_together': "(('source_content_type', 'source_object_id', 'target_content_type', 'target_object_id', 'name'),)", 'object_name': 'Relation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'source_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'relation_source_content_type'", 'to': u"orm['contenttypes.ContentType']"}),
            'source_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'target_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'relation_target_content_type'", 'to': u"orm['contenttypes.ContentType']"}),
            'target_object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'photologue.photo': {
            'Meta': {'ordering': "['-date_added']", 'object_name': 'Photo'},
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'crop_from': ('django.db.models.fields.CharField', [], {'default': "'center'", 'max_length': '10', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'effect': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'photo_related'", 'null': 'True', 'to': u"orm['photologue.PhotoEffect']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sites.Site']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'tags': ('photologue.models.TagField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60'}),
            'view_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'photologue.photoeffect': {
            'Meta': {'object_name': 'PhotoEffect'},
            'background_color': ('django.db.models.fields.CharField', [], {'default': "'#FFFFFF'", 'max_length': '7'}),
            'brightness': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'color': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'contrast': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'filters': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'reflection_size': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'reflection_strength': ('django.db.models.fields.FloatField', [], {'default': '0.6'}),
            'sharpness': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'transpose_method': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'})
        },
        u'publisher.publisher': {
            'Meta': {'object_name': 'Publisher'},
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    if USE_GIS:
        models.update({
        'atlas.city': {
            'Meta': {'ordering': "('name',)", 'object_name': 'City'},
            'coordinates': ('atlas.fields.CoordinateField', [], {'blank': 'True', 'null': 'True', 'geography': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['atlas.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['atlas.Region']", 'null': 'True', 'blank': 'True'})
        },
        'atlas.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country'},
            'border': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'blank': 'True', 'null': 'True', 'geography': 'True'}),
            'country_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'atlas.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('django.db.models.fields.TextField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['atlas.City']"}),
            'coordinates': ('atlas.fields.CoordinateField', [], {'blank': 'True', 'null': 'True', 'geography': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['atlas.Country']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'photo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['photologue.Photo']", 'null': 'True', 'blank': 'True'})
        },
        'atlas.region': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('country', 'code'),)", 'object_name': 'Region'},
            'border': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'blank': 'True', 'null': 'True', 'geography': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['atlas.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
        })
        models['jmbo.modelbase']['location'] = ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['atlas.Location']", 'null': 'True', 'blank': 'True'})

    complete_apps = ['jmbo']
