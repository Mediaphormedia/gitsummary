var RepoListItemView = Backbone.View.extend({
	tagName: 'li',
	events: {
		'click .addButton': 'saveOrg',
		'click .removeButton': 'removeRepo',
	},
	initialize: function() {
		_.bindAll(this, 'addOrg', 'addRepo');
		this.org_name = $(this.el).data('org_name');
		this.repo_name = $(this.el).data('repo_name');
		this.gh_api_url = $(this.el).data('gh_api_url');
		this.model = window.repoCollection.find(function(model) {
			return model.get('name') == this.repo_name;
		}, this);
		if (this.model == undefined) {
			this.model = this.createModel();
		}
		this.org = window.orgCollection.find(function(model) {
			return model.get('name') == this.org_name;
		}, this);
		if (this.org == undefined) {
			this.org = this.createOrg();
		}
		this.model.bind('change:resource_uri', this.showRemoveButton, this);
		this.model.bind('destroy', this.showAddButton, this);
		this.updateButton();
	},
	createModel: function() {
		return new Repo({
			'name': this.repo_name,
			'url': this.gh_api_url,
		});
	},
	createOrg: function() {
		return new Org({
			'name': this.org_name
		});
	},
	showAddButton: function() {
		this.model.set({'id': undefined, 'resource_uri': undefined});
		$(this.el).removeClass('active');
	},
	showRemoveButton: function() {
		$(this.el).addClass('active');
	},
	updateButton: function(e) {
		if (this.model.isNew()) {
			this.showAddButton();
		} else {
			this.showRemoveButton();
		}
	},
	saveOrg: function(e) {
		e.preventDefault();
		if (this.model.collection == undefined) {
			if (this.org.collection == undefined) {
				this.org.save({}, {
					success: this.addOrg
				});
			} else {
				this.addOrg();
			}
		}
	},
	addOrg: function(model) {
		window.orgCollection.add(model);
		this.model.save({'org': this.org.get('resource_uri')}, {
			success: this.addRepo
		});
	},
	addRepo: function(model) {
		window.repoCollection.add(model);
	},
	removeRepo: function(e) {
		e.preventDefault();
		this.model.destroy({success: function(model) {
			window.repoCollection.remove(model);
		}});
	}
})