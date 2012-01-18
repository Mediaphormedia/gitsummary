var ChangelogView = Backbone.View.extend({
	tagName: 'table',
	initialize: function() {
		this.org_name = $(this.el).attr('data-org_name');
		this.repo = $(this.el).attr('data-repo');
		this.user = $(this.el).attr('data-user');
		this.user_id = $(this.el).attr('data-user_id');
		this.commitViews = _.map(this.$('tr.commit'), function(elem) {
			return new CommentView({
				el: elem,
				parentView: this
			});
		}, this);
	}
})