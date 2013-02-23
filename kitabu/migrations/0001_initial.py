# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Validator'
        db.create_table('kitabu_validator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actual_validator_related_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('apply_to_all', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('kitabu', ['Validator'])

    def backwards(self, orm):
        # Deleting model 'Validator'
        db.delete_table('kitabu_validator')

    models = {
        'kitabu.validator': {
            'Meta': {'object_name': 'Validator'},
            'actual_validator_related_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'apply_to_all': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['kitabu']
