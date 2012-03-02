var SidebarView = Backbone.View.extend({
	tagName: 'ul',
	initialize: function(options) {
		this.collection = window.orgCollection;
		this.collection.bind('add', this.addOrg, this);
		this.collection.bind('remove', this.removeOrg, this);
		_.each(this.$('li.org'), function(org_elem) {
			id = $(org_elem).data('href');
			model = this.collection.get(id);
			org = new SidebarOrgView({
				parentView: this,
				model: model,
				el: org_elem
			});
		}, this);
	},
	addOrg: function(model) {
		org = new SidebarOrgView({
			parentView: this,
			model: model
		}).render();
		$(this.el).append(org.el);
	},
	removeOrg: function(model) {
		$(model.sideBarView.el).remove();
	}
});
