var GraphSpace = GraphSpace || {};

GraphSpace.Clock = (function() {
	var time = 0;
	var looper = 0;

	function start () {
		var self = this;
		this.looper = window.setInterval(function() {
            self.time++;
        }, 1000);
	};

	function stop() {
		clearInterval(this.looper);
		var timeSpent = this.time;
		this.time = 0;
		return timeSpent;
	};

    function convertToReadableTime(time) {
        var hours = parseInt(time/3600);

        if (hours < 10) {
            hours = "0" + hours;
        }

        var minutes = parseInt(time/60);

        if (minutes < 10) {
            minutes = "0" + minutes; 
        }

        var seconds = parseInt(time % 60);

        if (seconds < 10) {
            seconds = "0" + seconds;
        }

        return  hours + ":" + minutes + ":" + seconds;
    };
})();