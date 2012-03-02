var SidebarOrgView = Backbone.View.extend({
	tagName: 'li',
	className: 'org',
	template: _.template('<h6><%= org_name %></h6><ul class="unstyled"></ul>'),
	initialize: function(options) {
		this.parentView = options.parentView;
		this.collection = window.repoCollection;
		this.collection.bind('add', this.addRepo, this);
		this.collection.bind('remove', this.removeRepo, this);
		this.model.sideBarView = this;
		this.model.bind('destroy', this.removeOrg, this);
	},
	render: function() {
		org_id = this.model.get('id');
		org_name = this.model.get('name');
		var html = this.template({
	      'org_name': org_name
	    });
		$(this.el).attr({
			'data-name': org_name,
			'data-href': "/api/v1/"+org_id+"/"
		});
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
