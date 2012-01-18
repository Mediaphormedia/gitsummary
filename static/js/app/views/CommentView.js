var CommentView = Backbone.View.extend({
	tagName: 'tr',
	events: {
		'change input[name=include]': 'setInclude',
		'change input[name=include_commit_message]': 'setInclude',
		'click .readmore': 'toggleMessage'
	},
	initialize: function(options) {
		_.bindAll(this, 'saveText', 'addComment');
		this.parentView = options.parentView;
		this.commit_sha = $(this.el).attr('data-commit_sha');
		this.commit_datetime = new Date($(this.el).attr('data-commit_datetime'));
		this.collection = window.commentsCollection;
		this.textarea = this.$('textarea');
		this.model = this.collection.find(function(model) {
			return model.get('commit_sha') == this.commit_sha;
		}, this);
		if (this.model == undefined) {
			this.model = new Comment({
				'commit_sha': this.commit_sha,
				'commit_datetime': this.commit_datetime,
				'repo': this.parentView.repo,
				'author': this.parentView.user,
				'included_tickets': []
			});
		}
		this.model.bind('change', this.saveModel, this);
		setInterval(this.saveText, 500);

		this.ticketCollection = this.model.tickets;
		this.ticketViews = _.map(this.$('li.ticket'), function(elem) {
			return new TicketView({
				parentView: this,
				el: elem,
				collection: this.ticketCollection
			});
		}, this);
	},
	setInclude: function(e) {
		attrs = {};

		key = $(e.currentTarget).attr('name');
		value = $(e.currentTarget).is(':checked');
		attrs[key] = value
		this.model.set(attrs);
	},
	saveText: function() {
		value = this.textarea.val();
		this.model.set({'content': value})
	},
	commentHasData: function(model) {
		if (model.get('resource_uri') ||
		model.get('content') ||
		model.get('include') ||
		model.get('include_commit_message') ||
		model.get('included_tickets').length) {
			return true;
		}
		return false;
	},
	saveModel: function() {
		if (this.commentHasData(this.model)) {
			if (this.model.isNew()) {
				this.model.save({}, {success: this.addComment});
			} else {
				this.model.save();
			}
		}
	},
	addComment: function(model) {
		this.collection.add(model);
	},
	toggleMessage: function(e) {
		e.preventDefault();
		messageElement = this.$('.messageText');
		parentElement = $(e.currentTarget).parent();
		if (parentElement.hasClass('open')) {
			shortText = parentElement.attr('data-short_message');
			messageElement.text(shortText);
			parentElement.removeClass('open')
			$(e.currentTarget).text('read more');
		} else {
			fullText = $(e.currentTarget).parent().attr('title');
			messageElement.text(fullText);
			parentElement.addClass('open');
			$(e.currentTarget).text('close');
		}
	}
});
