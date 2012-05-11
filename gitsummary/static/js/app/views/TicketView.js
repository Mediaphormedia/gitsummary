var TicketView = Backbone.View.extend({
	tagName: 'li',
	events: {
		'change input[type=checkbox]': 'toggleInclude'
	},
	initialize: function(options) {
		this.parentView = options.parentView;
		_.bindAll(this, 'addTicket');
		number = parseInt($(this.el).data('number'));
		source = $(this.el).data('source');
		title = $(this.el).data('itle');
		resource_uri = $(this.el).data('resource_uri');
		if (this.$('input').is(':checked')) {
			this.model = this.parentView.model.tickets.get(resource_uri);
		} else {
			this.model = new Ticket({
				'number': number,
				'source': source,
				'repo': this.parentView.parentView.repo,
				'title': title,
				'resource_uri': resource_uri
			});
		}
	},
	toggleInclude: function(e) {
		value = $(e.currentTarget).is(':checked');
		if (value) {
			this.include();
		} else {
			this.remove();
		}
	},
	include: function() {
		this.addTicket(this.model);
	},
	addTicket: function(model) {
		if (model.get('resource_uri') && model.collection == undefined) {
			this.collection.add(model);
		} else {
			model.save({}, {success: this.addTicket})
		}
	},
	remove: function() {
		this.collection.remove(this.model);
	},

});
