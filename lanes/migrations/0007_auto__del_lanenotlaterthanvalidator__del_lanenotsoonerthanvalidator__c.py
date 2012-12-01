# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'LaneNotLaterThanValidator'
        db.delete_table('lanes_lanenotlaterthanvalidator')

        # Deleting model 'LaneNotSoonerThanValidator'
        db.delete_table('lanes_lanenotsoonerthanvalidator')

        # Changing field 'LaneWithinPeriodValidator.start'
        db.alter_column('lanes_lanewithinperiodvalidator', 'start', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'LaneWithinPeriodValidator.end'
        db.alter_column('lanes_lanewithinperiodvalidator', 'end', self.gf('django.db.models.fields.DateTimeField')(null=True))

    def backwards(self, orm):
        # Adding model 'LaneNotLaterThanValidator'
        db.create_table('lanes_lanenotlaterthanvalidator', (
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('validator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kitabu.Validator'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('lanes', ['LaneNotLaterThanValidator'])

        # Adding model 'LaneNotSoonerThanValidator'
        db.create_table('lanes_lanenotsoonerthanvalidator', (
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('validator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kitabu.Validator'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('lanes', ['LaneNotSoonerThanValidator'])

        # Changing field 'LaneWithinPeriodValidator.start'
        db.alter_column('lanes_lanewithinperiodvalidator', 'start', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 12, 1, 0, 0)))

        # Changing field 'LaneWithinPeriodValidator.end'
        db.alter_column('lanes_lanewithinperiodvalidator', 'end', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 12, 1, 0, 0)))

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
        'lanes.lanelateenoughvalidator': {
            'Meta': {'object_name': 'LaneLateEnoughValidator'},
            'time_unit': ('django.db.models.fields.CharField', [], {'default': "'second'", 'max_length': '6'}),
            'time_value': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
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
        'lanes.lanewithinperiodvalidator': {
            'Meta': {'object_name': 'LaneWithinPeriodValidator'},
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'})
        },
        'pools.pool': {
            'Meta': {'object_name': 'Pool'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['lanes']
