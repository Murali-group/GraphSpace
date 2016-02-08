var GraphSpace = GraphSpace || {};

GraphSpace.Clock = {
	time: 0,
	looper: 0,

	start: function() {
		var self = this;
		this.looper = window.setInterval(function() {
            self.time++;
        }, 1000);
	},

	stop: function() {
		clearInterval(this.looper);
		var timeSpent = this.time;
		this.time = 0;
		return timeSpent;
	}
};