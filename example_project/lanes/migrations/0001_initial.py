# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Lane'
        db.create_table(u'lanes_lane', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('validity_period', self.gf('django.db.models.fields.CharField')(default='60*60*24*3', max_length=13)),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(related_name='subjects', to=orm['pools.Pool'])),
        ))
        db.send_create_signal(u'lanes', ['Lane'])

        # Adding M2M table for field validators on 'Lane'
        db.create_table(u'lanes_lane_validators', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('lane', models.ForeignKey(orm[u'lanes.lane'], null=False)),
            ('validator', models.ForeignKey(orm['kitabu.validator'], null=False))
        ))
        db.create_unique(u'lanes_lane_validators', ['lane_id', 'validator_id'])

        # Adding model 'LaneReservation'
        db.create_table(u'lanes_lanereservation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('valid_until', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('exclusive', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reservations', to=orm['lanes.Lane'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='reservations', null=True, to=orm['lanes.LaneReservationGroup'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
        ))
        db.send_create_signal(u'lanes', ['LaneReservation'])

        # Adding model 'LaneReservationGroup'
        db.create_table(u'lanes_lanereservationgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'lanes', ['LaneReservationGroup'])

        # Adding model 'LFullTimeValidator'
        db.create_table(u'lanes_lfulltimevalidator', (
            (u'validator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kitabu.Validator'], unique=True, primary_key=True)),
            ('interval', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('interval_type', self.gf('django.db.models.fields.CharField')(max_length=6)),
        ))
        db.send_create_signal(u'lanes', ['LFullTimeValidator'])

        # Adding model 'LTimeIntervalValidator'
        db.create_table(u'lanes_ltimeintervalvalidator', (
            (u'validator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kitabu.Validator'], unique=True, primary_key=True)),
            ('time_value', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('time_unit', self.gf('django.db.models.fields.CharField')(default='second', max_length=6)),
            ('interval_type', self.gf('django.db.models.fields.CharField')(default='s', max_length=2)),
            ('check_end', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'lanes', ['LTimeIntervalValidator'])

        # Adding model 'LWithinPeriodValidator'
        db.create_table(u'lanes_lwithinperiodvalidator', (
            (u'validator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kitabu.Validator'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'lanes', ['LWithinPeriodValidator'])

        # Adding model 'Period'
        db.create_table(u'lanes_period', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('validator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='periods', to=orm['lanes.LWithinPeriodValidator'])),
        ))
        db.send_create_signal(u'lanes', ['Period'])

        # Adding model 'LNotWithinPeriodValidator'
        db.create_table(u'lanes_lnotwithinperiodvalidator', (
            (u'validator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kitabu.Validator'], unique=True, primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'lanes', ['LNotWithinPeriodValidator'])

        # Adding model 'LMaxReservationsPerUserValidator'
        db.create_table(u'lanes_lmaxreservationsperuservalidator', (
            (u'validator_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['kitabu.Validator'], unique=True, primary_key=True)),
            ('max_reservations_on_current_subject', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('max_reservations_on_all_subjects', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
        ))
        db.send_create_signal(u'lanes', ['LMaxReservationsPerUserValidator'])


    def backwards(self, orm):
        
        # Deleting model 'Lane'
        db.delete_table(u'lanes_lane')

        # Removing M2M table for field validators on 'Lane'
        db.delete_table('lanes_lane_validators')

        # Deleting model 'LaneReservation'
        db.delete_table(u'lanes_lanereservation')

        # Deleting model 'LaneReservationGroup'
        db.delete_table(u'lanes_lanereservationgroup')

        # Deleting model 'LFullTimeValidator'
        db.delete_table(u'lanes_lfulltimevalidator')

        # Deleting model 'LTimeIntervalValidator'
        db.delete_table(u'lanes_ltimeintervalvalidator')

        # Deleting model 'LWithinPeriodValidator'
        db.delete_table(u'lanes_lwithinperiodvalidator')

        # Deleting model 'Period'
        db.delete_table(u'lanes_period')

        # Deleting model 'LNotWithinPeriodValidator'
        db.delete_table(u'lanes_lnotwithinperiodvalidator')

        # Deleting model 'LMaxReservationsPerUserValidator'
        db.delete_table(u'lanes_lmaxreservationsperuservalidator')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 25, 15, 21, 40, 296528)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 25, 15, 21, 40, 296115)'}),
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
            'validators': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['kitabu.Validator']", 'symmetrical': 'False', 'blank': 'True'}),
            'validity_period': ('django.db.models.fields.CharField', [], {'default': "'60*60*24*3'", 'max_length': '13'})
        },
        u'lanes.lanereservation': {
            'Meta': {'object_name': 'LaneReservation'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'exclusive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reservations'", 'null': 'True', 'to': u"orm['lanes.LaneReservationGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reservations'", 'to': u"orm['lanes.Lane']"}),
            'valid_until': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
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
            'check_end': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
