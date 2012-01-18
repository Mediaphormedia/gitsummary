var TicketCollection = Backbone.Collection.extend({
	model: Ticket,
	url: '/api/v1/ticket/'
});
