$(document).ready(function() {

	alert('testing');
	$("#create_group").click(function(e) {
		e.preventDefault();

		var groupName = $("#group_name").val();

		if (groupName.length() == 0 || !groupName) {
			return alert("Please enter in a valid group name!");
		}

		alert(groupName);

		$.post('../add/' + groupName + '/', {
			"groupname": groupName,
			"username": $("#username").text()
		}, function (data) {
			alert(data);
		});
	});

	$(".delete").click(function (e) {
		alert($(this).attr('id'));
	});
});