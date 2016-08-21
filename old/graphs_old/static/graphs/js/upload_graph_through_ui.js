$(document).ready(function() {

	//Message to display to the user
	$("#files").text("No file chosen");

	//If user uploads a file, change message
	$("#graphname").on('change', function() {
		$("#files").text(getFileName($(this).val()));
	});

	//Upload the graph
	$("#upload_graph").click(function(e) {
		e.preventDefault();

		var email = $("#email").val();
		var graph = $("#graphname").val();

		if (graph.length == 0) {
			return alert("Please upload a valid cyjs graph!");
		}

		$("#upload_form").submit();
	});

	$("#create").click(function(e) {
		e.preventDefault();
		$("#createModal").modal('toggle');
	});

});

/**
* Gets file name of path of uploaded file and 
* notifies user that they chose a file.
*/
function getFileName(fullPath) {
	if (fullPath) {
		var startIndex = (fullPath.indexOf('\\') >= 0 ? fullPath.lastIndexOf('\\') : fullPath.lastIndexOf('/'));
		var filename = fullPath.substring(startIndex);
		if (filename.indexOf('\\') === 0 || filename.indexOf('/') === 0) {
			filename = filename.substring(1);
		}
		return filename;
	}
};