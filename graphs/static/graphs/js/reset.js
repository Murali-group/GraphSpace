$(document).ready(function() {

	var URL_PATH = $("#url").text();

	$("#reset_pw").click(function (e) {
		e.preventDefault();

		var password = $("#password").val()
		var verifyPass = $("#verifyPass").val()

		if (password.length == 0 || verifyPass.length == 0) {
			return alert("Please enter a password in both fields!");
		} else if (password !== verifyPass) {
			return alert("Please make sure both fields have the same value!");
		} else {
			$.post("../resetPassword/", {email: $("#reset_email").val(), password: password}, function (data) {

				if (data.Error) {
					return alert(data.Error);
				} else {
					alert(data.Success);
					window.location.href = URL_PATH + 'index/';
				}
			});
		}
	});
});
