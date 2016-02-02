// var Clock = {
// 	totalSeconds: 0,
// 	timeLeft: 0,

// 	setSeconds: function (seconds) {
// 		this.totalSeconds = seconds;
// 	},

// 	getSeconds: function() {
// 		return this.totalSeconds;
// 	},

// 	start: function (callback) {
// 	    var self = this;

// 	    var timer = self.getSeconds(), minutes, seconds;
//         this.timeLeft = setInterval(function() {
//             minutes = parseInt(timer / 60, 10);
//             seconds = parseInt(timer % 60, 10);

//             minutes = minutes < 10 ? "0" + minutes : minutes;
//             seconds = seconds < 10 ? "0" + seconds : seconds;

//             $("#timer").html(minutes + ":" + seconds);

//             if (--timer < 0) {
//                 $("#overlay").show();
//                 self.pause();
//                 callback();
//             } else {
//             	self.setSeconds(timer);
//             }

//         }, 1000);
// 	},

// 	pause: function () {
// 	    clearInterval(this.timeLeft);
// 	},

// 	reverse: function(callback) {
// 		this.totalSeconds += 10;
// 		this.pause();
// 		this.start(callback);

// 	},

// 	forward: function (callback) {
// 		this.pause();
// 		if (this.totalSeconds - 10 < 0) {
// 			this.totalSeconds = 0;
// 		} else {
// 			this.totalSeconds -= 10;
// 		}
// 		this.start(callback);
// 	}
// };

var Clock = {
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
		// return convertToReadableTime(timeSpent);
		return timeSpent;
	}
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
    }