# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'ReservationValidator.actual_instance_name'
        db.delete_column('kitabu_reservationvalidator', 'actual_instance_name')

        # Adding field 'ReservationValidator.actual_validator_related_name'
        db.add_column('kitabu_reservationvalidator', 'actual_validator_related_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200),
                      keep_default=False)

    def backwards(self, orm):
        # Adding field 'ReservationValidator.actual_instance_name'
        db.add_column('kitabu_reservationvalidator', 'actual_instance_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200),
                      keep_default=False)

        # Deleting field 'ReservationValidator.actual_validator_related_name'
        db.delete_column('kitabu_reservationvalidator', 'actual_validator_related_name')

    models = {
        'kitabu.reservationvalidator': {
            'Meta': {'object_name': 'ReservationValidator'},
            'actual_validator_related_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['kitabu']
