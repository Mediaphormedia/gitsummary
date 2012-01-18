var Comment = Backbone.Model.extend({
	urlRoot: '/api/v1/comment/',
	initialize: function() {
		this.tickets = new TicketCollection();
		this.tickets.reset(_.map(this.get('included_tickets'), function(ticket_uri) {
			model = new Ticket({
				'resource_uri': ticket_uri,
			});
			return model;
		}, this), {silent: true});
		this.tickets.each(function(ticket) { ticket.fetch(); });
		this.tickets.bind('add', this.addTicket, this);
		this.tickets.bind('remove', this.removeTicket, this);
		this.tickets.bind('change', this.updateTicket, this);
	},
	updateTicket: function(model) {
		this.trigger('change');
	},
	addTicket: function(model) {
		this.get('included_tickets').push(model.get('resource_uri'));
		this.trigger('change');
	},
	removeTicket: function(model) {
		included = this.get('included_tickets');
		filtered = _.reject(included, function(resource_uri) {
			return resource_uri == model.get('resource_uri');
		}, model);
		this.set({'included_tickets': filtered});
	}
});
