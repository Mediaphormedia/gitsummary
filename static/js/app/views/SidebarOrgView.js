var SidebarOrgView = Backbone.View.extend({
	tagName: 'li',
	className: 'org',
	template: _.template('<h6 data-href="/api/v1/<%= org_id %>/"><%= org_name %></h6><ul class="unstyled"></ul>'),
	initialize: function(options) {
		this.parentView = options.parentView;
		this.collection = window.repoCollection;
		this.collection.bind('add', this.addRepo, this);
		this.collection.bind('remove', this.removeRepo, this);
		this.model.sideBarView = this;
		this.model.bind('destroy', this.removeOrg, this);
	},
	render: function() {
		var html = this.template({
	      org_id: this.model.get('id'),
	      org_name: this.model.get('name')
	    });
		$(this.el).attr('data-name', this.model.get('name'));
	    $(this.el).append(html);
	    return this;
	},
	addRepo: function(model) {
		if (model.get('org') == this.model.get('resource_uri')) {
			repo =  new SidebarRepoView({
				parentView: this,
				model: model
			}).render();
			this.$('ul').append(repo.el);
		}
	},
	removeRepo: function(model) {
		repos = this.collection.filter(function(model) {
			return model.get('org') == this.model.get('resource_uri');
		}, this);
		if (repos.length == 0) {
			this.model.destroy();
		};
	},
	removeOrg: function(model) {
		$(this.el).remove();
		window.orgCollection.remove(model);
	}
});
