var CommentCollection = Backbone.Collection.extend({
	model: Comment,
	url: '/api/v1/comment/',
	comparator: function(model) {
		today = new Date();
		commit_date = Date.parse(model.get('commit_datetime'));
		return today.getTime() - commit_date.getTime();
	}
});
