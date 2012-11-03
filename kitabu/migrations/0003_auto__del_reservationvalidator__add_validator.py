# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'ReservationValidator'
        db.delete_table('kitabu_reservationvalidator')

        # Adding model 'Validator'
        db.create_table('kitabu_validator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_validator_related_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('kitabu', ['Validator'])

    def backwards(self, orm):
        # Adding model 'ReservationValidator'
        db.create_table('kitabu_reservationvalidator', (
            ('actual_validator_related_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('kitabu', ['ReservationValidator'])

        # Deleting model 'Validator'
        db.delete_table('kitabu_validator')

    models = {
        'kitabu.validator': {
            'Meta': {'object_name': 'Validator'},
            'actual_validator_related_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['kitabu']
