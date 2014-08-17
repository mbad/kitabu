# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IsolationTestSubject'
        db.create_table(u'kitabu_isolationtestsubject', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('kitabu', ['IsolationTestSubject'])

        # Adding model 'IsolationTestReservation'
        db.create_table(u'kitabu_isolationtestreservation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reservations', to=orm['kitabu.IsolationTestSubject'])),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('kitabu', ['IsolationTestReservation'])

        # Adding model 'Validator'
        db.create_table(u'kitabu_validator', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_validator_related_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('apply_to_all', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('kitabu', ['Validator'])


    def backwards(self, orm):
        # Deleting model 'IsolationTestSubject'
        db.delete_table(u'kitabu_isolationtestsubject')

        # Deleting model 'IsolationTestReservation'
        db.delete_table(u'kitabu_isolationtestreservation')

        # Deleting model 'Validator'
        db.delete_table(u'kitabu_validator')


    models = {
        'kitabu.isolationtestreservation': {
            'Meta': {'object_name': 'IsolationTestReservation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reservations'", 'to': "orm['kitabu.IsolationTestSubject']"})
        },
        'kitabu.isolationtestsubject': {
            'Meta': {'object_name': 'IsolationTestSubject'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'kitabu.validator': {
            'Meta': {'object_name': 'Validator'},
            'actual_validator_related_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'apply_to_all': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['kitabu']