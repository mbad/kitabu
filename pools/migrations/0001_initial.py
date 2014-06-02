# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    needed_by = (
        ("lanes", "0001_initial"),
    )

    def forwards(self, orm):
        # Adding model 'Pool'
        db.create_table('pools_pool', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('pools', ['Pool'])

    def backwards(self, orm):
        # Deleting model 'Pool'
        db.delete_table('pools_pool')

    models = {
        'pools.pool': {
            'Meta': {'object_name': 'Pool'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['pools']
