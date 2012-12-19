# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'LaneWithinPeriodValidator.start'
        db.delete_column('lanes_lanewithinperiodvalidator', 'start')

        # Deleting field 'LaneWithinPeriodValidator.end'
        db.delete_column('lanes_lanewithinperiodvalidator', 'end')


    def backwards(self, orm):
        
        # Adding field 'LaneWithinPeriodValidator.start'
        db.add_column('lanes_lanewithinperiodvalidator', 'start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)

        # Adding field 'LaneWithinPeriodValidator.end'
        db.add_column('lanes_lanewithinperiodvalidator', 'end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True), keep_default=False)


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 12, 19, 13, 58, 27, 464199)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 12, 19, 13, 58, 27, 464132)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'kitabu.validator': {
            'Meta': {'object_name': 'Validator'},
            'actual_validator_related_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'apply_to_all': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'lanes.lane': {
            'Meta': {'object_name': 'Lane'},
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subjects'", 'to': "orm['pools.Pool']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'validators': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['kitabu.Validator']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'lanes.lanefulltimevalidator': {
            'Meta': {'object_name': 'LaneFullTimeValidator'},
            'interval': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'interval_type': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'})
        },
        'lanes.lanenotwithinperiodvalidator': {
            'Meta': {'object_name': 'LaneNotWithinPeriodValidator'},
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'})
        },
        'lanes.lanereservation': {
            'Meta': {'object_name': 'LaneReservation'},
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reservations'", 'null': 'True', 'to': "orm['lanes.LaneReservationGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reservations'", 'to': "orm['lanes.Lane']"})
        },
        'lanes.lanereservationgroup': {
            'Meta': {'object_name': 'LaneReservationGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'lanes.lanetimeintervalvalidator': {
            'Meta': {'object_name': 'LaneTimeIntervalValidator'},
            'interval_type': ('django.db.models.fields.CharField', [], {'default': "'s'", 'max_length': '2'}),
            'time_unit': ('django.db.models.fields.CharField', [], {'default': "'second'", 'max_length': '6'}),
            'time_value': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'})
        },
        'lanes.lanewithinperiodvalidator': {
            'Meta': {'object_name': 'LaneWithinPeriodValidator'},
            'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'})
        },
        'pools.pool': {
            'Meta': {'object_name': 'Pool'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['lanes']
