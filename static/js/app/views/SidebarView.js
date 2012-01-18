var SidebarView = Backbone.View.extend({
	tagName: 'ul',
	initialize: function(options) {
		this.collection = window.orgCollection;
		this.collection.bind('add', this.addOrg, this);
		this.collection.bind('remove', this.removeOrg, this);
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
