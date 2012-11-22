# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding field 'Validator.apply_to_all'
        db.add_column('kitabu_validator', 'apply_to_all', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

    def backwards(self, orm):

        # Deleting field 'Validator.apply_to_all'
        db.delete_column('kitabu_validator', 'apply_to_all')

    models = {
        'kitabu.validator': {
            'Meta': {'object_name': 'Validator'},
            'actual_validator_related_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'apply_to_all': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['kitabu']
