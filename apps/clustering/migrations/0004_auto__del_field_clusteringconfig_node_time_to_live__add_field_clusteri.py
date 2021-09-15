# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'ClusteringConfig.node_time_to_live'
        db.delete_column('clustering_clusteringconfig', 'node_time_to_live')

        # Adding field 'ClusteringConfig.node_heartbeat_timeout'
        db.add_column('clustering_clusteringconfig', 'node_heartbeat_timeout',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=5),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'ClusteringConfig.node_time_to_live'
        db.add_column('clustering_clusteringconfig', 'node_time_to_live',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=5),
                      keep_default=False)

        # Deleting field 'ClusteringConfig.node_heartbeat_timeout'
        db.delete_column('clustering_clusteringconfig', 'node_heartbeat_timeout')


    models = {
        'clustering.clusteringconfig': {
            'Meta': {'object_name': 'ClusteringConfig'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lock_id': ('django.db.models.fields.CharField', [], {'default': '1', 'unique': 'True', 'max_length': '1'}),
            'node_heartbeat_interval': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'node_heartbeat_timeout': ('django.db.models.fields.PositiveIntegerField', [], {'default': '5'})
        },
        'clustering.node': {
            'Meta': {'object_name': 'Node'},
            'cpuload': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'}),
            'heartbeat': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 8, 1, 0, 0)', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memory_usage': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'blank': 'True'})
        }
    }

    complete_apps = ['clustering']