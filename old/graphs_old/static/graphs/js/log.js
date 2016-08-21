var GraphSpace = GraphSpace || {};

GraphSpace.Logger = {
	eventType: "",
	eventTime: "",
	elementInvolved: "",
	logEvents: [],

	addEvent: function(event) {

		var newEvent = {
			"eventType": event.type,
			"eventTime": event.timeStamp,
			"elementInvolved": event.target
		};

		if ($(event.target).val().length > 0) {
			newEvent["elementInvolved"] = $(event.target).val();
		} else if ($(event.target).attr('id') !== undefined) {
			newEvent["elementInvolved"] = $(event.target).attr('id')
		} else {
			newEvent["elementInvolved"] = "canvas"
		}

		this.logEvents.push(newEvent);
	},

	getEvents: function() {
		return this.logEvents;
	}

};