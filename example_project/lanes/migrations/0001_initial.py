# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Lane'
        db.create_table('lanes_lane', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(related_name='subjects', to=orm['pools.Pool'])),
        ))
        db.send_create_signal('lanes', ['Lane'])

        # Adding M2M table for field validators on 'Lane'
        db.create_table('lanes_lane_validators', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('lane', models.ForeignKey(orm['lanes.lane'], null=False)),
            ('validator', models.ForeignKey(orm['kitabu.validator'], null=False))
        ))
        db.create_unique('lanes_lane_validators', ['lane_id', 'validator_id'])

        # Adding model 'LaneReservation'
        db.create_table('lanes_lanereservation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('exclusive', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reservations', to=orm['lanes.Lane'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='reservations', null=True, to=orm['lanes.LaneReservationGroup'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
        ))
        db.send_create_signal('lanes', ['LaneReservation'])

        # Adding model 'LaneReservationGroup'
        db.create_table('lanes_lanereservationgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('lanes', ['LaneReservationGroup'])

        # Adding model 'LFullTimeValidator'
        db.create_table('lanes_lfulltimevalidator', (
            ('validator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kitabu.Validator'], unique=True, primary_key=True)),
            ('interval', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('interval_type', self.gf('django.db.models.fields.CharField')(max_length=6)),
        ))
        db.send_create_signal('lanes', ['LFullTimeValidator'])

        # Adding model 'LTimeIntervalValidator'
        db.create_table('lanes_ltimeintervalvalidator', (
            ('validator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kitabu.Validator'], unique=True, primary_key=True)),
            ('time_value', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('time_unit', self.gf('django.db.models.fields.CharField')(default='second', max_length=6)),
            ('interval_type', self.gf('django.db.models.fields.CharField')(default='s', max_length=2)),
        ))
        db.send_create_signal('lanes', ['LTimeIntervalValidator'])

        # Adding model 'LWithinPeriodValidator'
        db.create_table('lanes_lwithinperiodvalidator', (
            ('validator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kitabu.Validator'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('lanes', ['LWithinPeriodValidator'])

        # Adding model 'Period'
        db.create_table('lanes_period', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('validator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='periods', to=orm['lanes.LWithinPeriodValidator'])),
        ))
        db.send_create_signal('lanes', ['Period'])

        # Adding model 'LNotWithinPeriodValidator'
        db.create_table('lanes_lnotwithinperiodvalidator', (
            ('validator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kitabu.Validator'], unique=True, primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('lanes', ['LNotWithinPeriodValidator'])

        # Adding model 'LGivenHoursAndWeekdaysValidator'
        db.create_table('lanes_lgivenhoursandweekdaysvalidator', (
            ('validator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kitabu.Validator'], unique=True, primary_key=True)),
            ('monday', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('tuesday', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('wednesday', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('thursday', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('friday', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('saturday', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('sunday', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('lanes', ['LGivenHoursAndWeekdaysValidator'])

        # Adding model 'LMaxReservationsPerUserValidator'
        db.create_table('lanes_lmaxreservationsperuservalidator', (
            ('validator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kitabu.Validator'], unique=True, primary_key=True)),
            ('max_reservations_on_current_subject', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('max_reservations_on_all_subjects', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
        ))
        db.send_create_signal('lanes', ['LMaxReservationsPerUserValidator'])

    def backwards(self, orm):
        # Deleting model 'Lane'
        db.delete_table('lanes_lane')

        # Removing M2M table for field validators on 'Lane'
        db.delete_table('lanes_lane_validators')

        # Deleting model 'LaneReservation'
        db.delete_table('lanes_lanereservation')

        # Deleting model 'LaneReservationGroup'
        db.delete_table('lanes_lanereservationgroup')

        # Deleting model 'LFullTimeValidator'
        db.delete_table('lanes_lfulltimevalidator')

        # Deleting model 'LTimeIntervalValidator'
        db.delete_table('lanes_ltimeintervalvalidator')

        # Deleting model 'LWithinPeriodValidator'
        db.delete_table('lanes_lwithinperiodvalidator')

        # Deleting model 'Period'
        db.delete_table('lanes_period')

        # Deleting model 'LNotWithinPeriodValidator'
        db.delete_table('lanes_lnotwithinperiodvalidator')

        # Deleting model 'LGivenHoursAndWeekdaysValidator'
        db.delete_table('lanes_lgivenhoursandweekdaysvalidator')

        # Deleting model 'LMaxReservationsPerUserValidator'
        db.delete_table('lanes_lmaxreservationsperuservalidator')

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
        'lanes.lanereservation': {
            'Meta': {'object_name': 'LaneReservation'},
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'exclusive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reservations'", 'null': 'True', 'to': "orm['lanes.LaneReservationGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reservations'", 'to': "orm['lanes.Lane']"})
        },
        'lanes.lanereservationgroup': {
            'Meta': {'object_name': 'LaneReservationGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'lanes.lfulltimevalidator': {
            'Meta': {'object_name': 'LFullTimeValidator'},
            'interval': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'interval_type': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'})
        },
        'lanes.lgivenhoursandweekdaysvalidator': {
            'Meta': {'object_name': 'LGivenHoursAndWeekdaysValidator'},
            'friday': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'monday': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'saturday': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'sunday': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'thursday': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'tuesday': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'}),
            'wednesday': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'lanes.lmaxreservationsperuservalidator': {
            'Meta': {'object_name': 'LMaxReservationsPerUserValidator'},
            'max_reservations_on_all_subjects': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'max_reservations_on_current_subject': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'})
        },
        'lanes.lnotwithinperiodvalidator': {
            'Meta': {'object_name': 'LNotWithinPeriodValidator'},
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'})
        },
        'lanes.ltimeintervalvalidator': {
            'Meta': {'object_name': 'LTimeIntervalValidator'},
            'interval_type': ('django.db.models.fields.CharField', [], {'default': "'s'", 'max_length': '2'}),
            'time_unit': ('django.db.models.fields.CharField', [], {'default': "'second'", 'max_length': '6'}),
            'time_value': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'})
        },
        'lanes.lwithinperiodvalidator': {
            'Meta': {'object_name': 'LWithinPeriodValidator'},
            'validator_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['kitabu.Validator']", 'unique': 'True', 'primary_key': 'True'})
        },
        'lanes.period': {
            'Meta': {'object_name': 'Period'},
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'validator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'periods'", 'to': "orm['lanes.LWithinPeriodValidator']"})
        },
        'pools.pool': {
            'Meta': {'object_name': 'Pool'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['lanes']
