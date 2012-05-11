var SidebarRepoView = Backbone.View.extend({
	tagName: 'li',
	className: 'repo',
	template: _.template('<a id="<%= repo_name %>_ldmk" href="/repos/<%= org_name %>/<%= repo_name %>/changelog/"><%= repo_name %></a>'),
	initialize: function(options) {
		this.parentView = options.parentView;
		this.model.sidebarView = this;
		this.model.bind('destroy', this.destroy, this);
	},
	render: function() {
		var html = this.template({
	      repo_name: this.model.get('name'),
	      org_name: this.parentView.model.get('name')
	    });
	    $(this.el).attr('data-name', this.model.get('name'));
	    $(this.el).append(html);
	    return this;
	},
	destroy: function(model) {
		$(this.el).remove();
	}
});