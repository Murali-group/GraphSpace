var Logger = {
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
		}
		this.logEvents.push(newEvent);
	},

	getEvents: function() {
		return this.logEvents;
	}

};