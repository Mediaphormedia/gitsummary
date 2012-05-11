# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Org'
        db.create_table('changelog_org', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='orgs', to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('changelog', ['Org'])

        # Adding unique constraint on 'Org', fields ['user', 'name']
        db.create_unique('changelog_org', ['user_id', 'name'])

        # Adding model 'Repo'
        db.create_table('changelog_repo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('org', self.gf('django.db.models.fields.related.ForeignKey')(related_name='repos', to=orm['changelog.Org'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('changelog', ['Repo'])

        # Adding unique constraint on 'Repo', fields ['org', 'name']
        db.create_unique('changelog_repo', ['org_id', 'name'])

        # Adding model 'RepoSetting'
        db.create_table('changelog_reposetting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('repo', self.gf('django.db.models.fields.related.ForeignKey')(related_name='setting_set', unique=True, to=orm['changelog.Repo'])),
            ('ticket_regex', self.gf('django.db.models.fields.CharField')(default='#(\\d{2,4})', max_length=200)),
            ('messages_regex', self.gf('django.db.models.fields.CharField')(default='(close|fix|address|ticket)', max_length=200)),
            ('deploy_regex', self.gf('django.db.models.fields.CharField')(default='^refs/tags/deploy', max_length=200)),
            ('deploy_datetime_regex', self.gf('django.db.models.fields.CharField')(default='(\\d{4})/(\\d{2})/(\\d{2})/(\\d{2})(\\d{2})(\\d{2})', max_length=200)),
            ('timezone', self.gf('timezones.fields.TimeZoneField')(default='America/Chicago')),
            ('changelog_template', self.gf('django.db.models.fields.TextField')(default="<% _.each(comments, function(comment) { %><% if (comment.tickets.length) { %><% comment.tickets.each(function(ticket) { %><%= ticket.get('title') %><% }); %>. <% } %><%= comment.get('content') %>\n\n<% }); %>\n")),
        ))
        db.send_create_signal('changelog', ['RepoSetting'])

        # Adding model 'Ticket'
        db.create_table('changelog_ticket', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('number', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('repo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['changelog.Repo'])),
        ))
        db.send_create_signal('changelog', ['Ticket'])

        # Adding unique constraint on 'Ticket', fields ['source', 'number', 'repo']
        db.create_unique('changelog_ticket', ['source', 'number', 'repo_id'])

        # Adding model 'Comment'
        db.create_table('changelog_comment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('commit_sha', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('commit_datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('repo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['changelog.Repo'])),
            ('include', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('include_commit_message', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('changelog', ['Comment'])

        # Adding M2M table for field included_tickets on 'Comment'
        db.create_table('changelog_comment_included_tickets', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('comment', models.ForeignKey(orm['changelog.comment'], null=False)),
            ('ticket', models.ForeignKey(orm['changelog.ticket'], null=False))
        ))
        db.create_unique('changelog_comment_included_tickets', ['comment_id', 'ticket_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Ticket', fields ['source', 'number', 'repo']
        db.delete_unique('changelog_ticket', ['source', 'number', 'repo_id'])

        # Removing unique constraint on 'Repo', fields ['org', 'name']
        db.delete_unique('changelog_repo', ['org_id', 'name'])

        # Removing unique constraint on 'Org', fields ['user', 'name']
        db.delete_unique('changelog_org', ['user_id', 'name'])

        # Deleting model 'Org'
        db.delete_table('changelog_org')

        # Deleting model 'Repo'
        db.delete_table('changelog_repo')

        # Deleting model 'RepoSetting'
        db.delete_table('changelog_reposetting')

        # Deleting model 'Ticket'
        db.delete_table('changelog_ticket')

        # Deleting model 'Comment'
        db.delete_table('changelog_comment')

        # Removing M2M table for field included_tickets on 'Comment'
        db.delete_table('changelog_comment_included_tickets')


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
        'changelog.comment': {
            'Meta': {'object_name': 'Comment'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'commit_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'commit_sha': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'include_commit_message': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'included_tickets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['changelog.Ticket']", 'symmetrical': 'False'}),
            'repo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['changelog.Repo']"})
        },
        'changelog.org': {
            'Meta': {'unique_together': "(('user', 'name'),)", 'object_name': 'Org'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'orgs'", 'to': "orm['auth.User']"})
        },
        'changelog.repo': {
            'Meta': {'unique_together': "(('org', 'name'),)", 'object_name': 'Repo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'org': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'repos'", 'to': "orm['changelog.Org']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'changelog.reposetting': {
            'Meta': {'object_name': 'RepoSetting'},
            'changelog_template': ('django.db.models.fields.TextField', [], {'default': '"<% _.each(comments, function(comment) { %><% if (comment.tickets.length) { %><% comment.tickets.each(function(ticket) { %><%= ticket.get(\'title\') %><% }); %>. <% } %><%= comment.get(\'content\') %>\\n\\n<% }); %>\\n"'}),
            'deploy_datetime_regex': ('django.db.models.fields.CharField', [], {'default': "'(\\\\d{4})/(\\\\d{2})/(\\\\d{2})/(\\\\d{2})(\\\\d{2})(\\\\d{2})'", 'max_length': '200'}),
            'deploy_regex': ('django.db.models.fields.CharField', [], {'default': "'^refs/tags/deploy'", 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'messages_regex': ('django.db.models.fields.CharField', [], {'default': "'(close|fix|address|ticket)'", 'max_length': '200'}),
            'repo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'setting_set'", 'unique': 'True', 'to': "orm['changelog.Repo']"}),
            'ticket_regex': ('django.db.models.fields.CharField', [], {'default': "'#(\\\\d{2,4})'", 'max_length': '200'}),
            'timezone': ('timezones.fields.TimeZoneField', [], {'default': "'America/Chicago'"})
        },
        'changelog.ticket': {
            'Meta': {'unique_together': "(('source', 'number', 'repo'),)", 'object_name': 'Ticket'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'repo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['changelog.Repo']"}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['changelog']
