$(document).ready(function() {

	var URL_PATH = $("#url").text();

	//Gets query variables from the url
	function getQueryVariable(variable)
	{
	   var query = window.location.search.substring(1);
	   var vars = query.split("&");
	   for (var i=0;i<vars.length;i++) {
	           var pair = vars[i].split("=");
	           if(pair[0] == variable){return pair[1];}
	   }
	   return(false);
	}

	/**
	 * When clicked, it resets the password for given user.
	 */
	$("#reset").click(function(e) {
		e.preventDefault();

		var password = $("#pass").val()
		var verifyPass = $("#verifPass").val()

		var resetCode = getQueryVariable("id");

		if (!resetCode) {
			alert("Invalid reset code provided for this user!");
		}

		//If there is a password and verify password that are both the same
		if (password.length == 0 || verifyPass.length == 0) {
			return alert("Please enter a password in both fields!");
		} else if (password !== verifyPass) {
			return alert("Please make sure both fields have the same value!");
		} else {
			//Send reset request via email
			$.post("../resetPassword/", {
				email: $("#reset_email").val(),
				password: password,
				code: resetCode
			}, function(data) {

				if (data.Error) {
					console.log(data);
					return alert(data.Error);
				} else {
					alert("Password Updated!");
					window.location.href = URL_PATH + 'index/';
				}
			});
		}
	});
});