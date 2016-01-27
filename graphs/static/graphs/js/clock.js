var Clock = {
	totalSeconds: 0,
	timeLeft: 0,

	setSeconds: function (seconds) {
		this.totalSeconds = seconds;
	},

	getSeconds: function() {
		return this.totalSeconds;
	},

	start: function (callback) {
	    var self = this;

	    var timer = self.getSeconds(), minutes, seconds;
        this.timeLeft = setInterval(function() {
            minutes = parseInt(timer / 60, 10);
            seconds = parseInt(timer % 60, 10);

            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            $("#timer").html(minutes + ":" + seconds);

            if (--timer < 0) {
                $("#overlay").show();
                self.pause();
                callback();
            } else {
            	self.setSeconds(timer);
            }

        }, 1000);
	},

	pause: function () {
	    clearInterval(this.timeLeft);
	},

	reverse: function(callback) {
		this.totalSeconds += 10;
		this.pause();
		this.start(callback);

	},

	forward: function (callback) {
		this.pause();
		if (this.totalSeconds - 10 < 0) {
			this.totalSeconds = 0;
		} else {
			this.totalSeconds -= 10;
		}
		this.start(callback);
	}
};