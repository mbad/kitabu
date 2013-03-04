# -*- coding: utf-8 -*-
from south.v2 import DataMigration


class Migration(DataMigration):

    def forwards(self, orm):
        orm['kitabu.Validator'].objects.filter(actual_validator_related_name='lgivenhoursandweekdaysvalidator').delete()

    def backwards(self, orm):
        pass

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'kitabu.validator': {
            'Meta': {'object_name': 'Validator'},
            'actual_validator_related_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'apply_to_all': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'lanes.lane': {
            'Meta': {'object_name': 'Lane'},
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subjects'", 'to': u"orm['pools.Pool']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'validators': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['kitabu.Validator']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'lanes.lanereservation': {
            'Meta': {'object_name': 'LaneReservation'},
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'exclusive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reservations'", 'null': 'True', 'to': u"orm['lanes.LaneReservationGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reservations'", 'to': u"orm['lanes.Lane']"})
        },
        u'lanes.lanereservationgroup': {
            'Meta': {'object_name': 'LaneReservationGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'lanes.lfulltimevalidator': {
            'Meta': {'object_name': 'LFullTimeValidator'},
            'interval': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'interval_type': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            u'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'lanes.lmaxreservationsperuservalidator': {
            'Meta': {'object_name': 'LMaxReservationsPerUserValidator'},
            'max_reservations_on_all_subjects': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'max_reservations_on_current_subject': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            u'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'lanes.lnotwithinperiodvalidator': {
            'Meta': {'object_name': 'LNotWithinPeriodValidator'},
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            u'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'lanes.ltimeintervalvalidator': {
            'Meta': {'object_name': 'LTimeIntervalValidator'},
            'interval_type': ('django.db.models.fields.CharField', [], {'default': "'s'", 'max_length': '2'}),
            'time_unit': ('django.db.models.fields.CharField', [], {'default': "'second'", 'max_length': '6'}),
            'time_value': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            u'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'lanes.lwithinperiodvalidator': {
            'Meta': {'object_name': 'LWithinPeriodValidator'},
            u'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'lanes.period': {
            'Meta': {'object_name': 'Period'},
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'validator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'periods'", 'to': u"orm['lanes.LWithinPeriodValidator']"})
        },
        u'pools.pool': {
            'Meta': {'object_name': 'Pool'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['lanes']
    symmetrical = True
