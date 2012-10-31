# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ReservationValidator'
        db.create_table('kitabu_reservationvalidator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_instance_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('kitabu', ['ReservationValidator'])


    def backwards(self, orm):
        # Deleting model 'ReservationValidator'
        db.delete_table('kitabu_reservationvalidator')


    models = {
        'kitabu.reservationvalidator': {
            'Meta': {'object_name': 'ReservationValidator'},
            'actual_instance_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['kitabu']