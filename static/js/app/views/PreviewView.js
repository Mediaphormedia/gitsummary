var PreviewView = Backbone.View.extend({
	events: {
		'keyup #templateCode': 'render',
		'click #templateBtn': 'toggleTemplate'
	},
	initialize: function(options) {
		_.bindAll(this, 'bindSetting', 'saveSetting');
		this.parentView = options.parentView;
		this.collection = window.commentsCollection;
		this.collection.bind('change', this.updatePreview, this);
		this.templateElement = this.$('#templateCode');
		this.template_content = '';
		this.setting = new RepoSetting({
			'resource_uri': this.templateElement.attr('data-reposetting')
		});
		this.setting.fetch({'success': this.bindSetting});
		this.output = this.$('#output');
		this.updatePreview();
	},
	render: function(e) {
		this.template_content = this.templateElement.val();
		this.template = _.template(this.template_content);
		comments = this.collection.filter(function(model) {
			return model.get('include');
		});
		if (comments.length) {
			try {
				text = this.template({
					comments: comments
				});
				this.output.val(text);				
			} catch(err) {
				this.output.val("Template error:\r\n" + err.line + ': ' + err.message);
			}
		};
	},
	updatePreview: function() {
		this.render();
	},
	bindSetting: function(model) {
		this.template_content = model.get('changelog_template');
		setInterval(this.saveSetting, 250);		
	},
	saveSetting: function() {
		if (this.setting.get('changelog_template') != this.template_content) {
			this.setting.save({'changelog_template': this.template_content});
		};
	},
	toggleTemplate: function(e) {
		e.preventDefault();
		if (this.templateElement.parent().hasClass('open')) {
			this.templateElement.parent().removeClass('open');
			this.templateElement.blur();
		} else {
			this.templateElement.parent().addClass('open');
			this.templateElement.focus();
		}
	}
});
