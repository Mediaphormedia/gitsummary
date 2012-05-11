var OrgCollection = Backbone.Collection.extend({
	model: Org,
	url: '/api/v1/org/'
});
