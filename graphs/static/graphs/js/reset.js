$(document).ready(function() {

	var URL_PATH = $("#url").text();

	/**
	 * When clicked, it resets the password for given user.
	 */
	$("#reset_pw").click(function(e) {
		e.preventDefault();

		var password = $("#password").val()
		var verifyPass = $("#verifyPass").val()

		//If there is a password and verify password that are both the same
		if (password.length == 0 || verifyPass.length == 0) {
			return alert("Please enter a password in both fields!");
		} else if (password !== verifyPass) {
			return alert("Please make sure both fields have the same value!");
		} else {
			//Send reset request via email
			$.post("../resetPassword/", {
				email: $("#reset_email").val(),
				password: password
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