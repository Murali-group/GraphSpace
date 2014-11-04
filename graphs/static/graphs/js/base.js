/*
 * This class is used for AJAX requests to log in/forgot/create account.
 */
$(document).ready(function() {

	$("#register").click(function (e) {
		e.preventDefault();
		var user_id = $("#user_id").val();
		var password = $("#password").val();
		var verify_password = $("#verify_password").val();

		if (!$("#user_id") || user_id.length == 0) {
			alert("Please enter your email!");
			return;
		} 

		if (!$("#password") || password.length == 0) {
			alert("Please enter a password for the account!");
			return;
		}

		if (!$("#verify_password") || verify_password.length == 0) {
			alert("Please re-enter your passwod");
			return;
		}

		if (password !== verify_password) {
			alert("Passwords do not match!");
			return;
		}

		var submitRequest = {
			"user_id": user_id,
			"password": password
		};

		$.post("/register/", submitRequest, function (data) {
			if (data.Error) {
				alert(data.Error);
			} else {
				alert("Account Created!");
				window.location.href = "/index";
			}
		});
	});

	$("#signin").click(function (e) {
		e.preventDefault();
		var email = $("#email").val();
		var pw = $("#pw").val();

		if (!$("#email") || email.length == 0) {
			alert("Please enter email!");
			return;
		}

		if (!$("#pw") || pw.length == 0) {
			alert("Please enter password!");
			return;
		}

		var loginInfo = {
			"user_id": email,
			"pw": pw
		};

		$.post("/index/", loginInfo, function (data) {
			if (data.Error) {
				alert(data.Error);
			} else {
				$("body").html(data);
			}
		});
	});

	$("#forgot_send").click(function (e) {
		e.preventDefault();

		var email = $("#forgot_email").val();

		if (!$("#forgot_email") || email.length == 0) {
			alert("Please enter your email!");
			return;
		}

		var forgotRequest = {
			"forgot_email": email
		};

		$.post("/forgot/", forgotRequest, function (data) {

			if (data.error) {
				alert(data.error);
			} else {
				window.location.href = "/index/";
			}
		});
	});

	$("#reset_pw").click(function (e) {
		e.preventDefault();

		var pass = $("#password").val();
		var verifyPass = $("#verifyPass").val();

		if (!pass || !verifyPass || pass.length == 0 || verifyPass.length == 0 || pass != verifyPass) {
			alert("Please enter a new password that matches both fields!");
		} else {
			var newPass = {
				"user_id": $("#reset_email").val(),
				"pass": pass
			};

			$.post("/reset/", newPass, function (data) {
				if (data.Error) {
					alert(data.Error);
				} else {
					window.location.href = "/index/";
					alert("Password updated!");
				}
			});
		}
	});

	$("#add_graph").click(function() {
		window.location.href = "/graphs/create";
	});

	$("input[name='shared']").on("change", function () {
	    if (this.value === 'private') {
	    	$("#shared_groups").css('display', 'block');
	    } else {
	    	$("#shared_groups").css('display', 'none');
	    }
	});

	$("#submit_graph").click(function(e) {
		e.preventDefault();
		var graphName = $("#graph_name").val();
		var tags = $("#tags").val();
		var priv = $("#shared")
		var pub = $("#shared2");
		var groups = $("#groups").val();

		if (!graphName || graphName.length == 0) {
			alert("Please enter a name for the graph!");
			return;
		}

		// var newGraph = {
		// 	"graph_name": graphName,
		// 	"tags": tags,
		// 	"graph_desc": "testing",
		// 	"graph_json": gra

		// };

		// $.post("/graphs/create", newGraph, function (data) {
		// 	if (data.Error) {
		// 		alert(data.Error);
		// 		return;
		// 	} else {
		// 		window.href.location = "/index/";
		// 	}
		// });

		$("#add_graph_form").submit();
	});

});