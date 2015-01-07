$(document).ready(function() {

    //these accordions make up the side menu
   $('#accordion_tags').accordion({
      collapsible: true,
   });

   $("#search_button").click(function (e) {
   	e.preventDefault();
   	var searchVal = $("#searching").val();
   	if (searchVal && searchVal.length > 0) {
   		if (document.URL.indexOf('tags=') == -1) {
   			if (document.URL.indexOf('?search=') == -1) {
   				window.location.href = document.URL + '?search=' + searchVal;
			} else {
				window.location.href = document.URL.substring(0, document.URL.indexOf('?search=') - 1) + '?search=' + searchVal;
			}
   		} else {
   			tagIndex = document.URL.indexOf('tags=');
   			searchIndex = document.URL.indexOf('search=');
   			if (searchIndex > tagIndex) {
   				window.location.href = document.URL.substring(0, searchIndex-1) + '&search=' + searchVal;
   			} else {
   				window.location.href = document.URL.substring(0, searchIndex-1) + '?' + document.URL.substring(tagIndex, document.URL.length) + '&search=' + searchVal;
   			}
   		}
   	} else {
   		alert("Please enter a term to search for!");
   		return;
   	}
   });

   $("#tags_button").click(function (e) {
   	e.preventDefault();
   	var searchVal = $("#tags_searching").val();
   	if (searchVal && searchVal.length > 0) {
   		if (document.URL.indexOf('search=') == -1) {
   			if (document.URL.indexOf('?tags=') == -1) {
   				window.location.href = document.URL + '?tags=' + searchVal;
			} else {
				window.location.href = document.URL.substring(0, document.URL.indexOf('?tags=') - 1) + '?tags=' + searchVal;
			}
   		} else {
   			tagIndex = document.URL.indexOf('tags=');
   			searchIndex = document.URL.indexOf('search=');
   			if (tagIndex > searchIndex) {
   				window.location.href = document.URL.substring(0, tagIndex-1) + '&tags=' + searchVal;
   			} else {
   				window.location.href = document.URL.substring(0, tagIndex-1) + '?' + document.URL.substring(searchIndex, document.URL.length) + '&tags=' + searchVal;
   			}
   		}
   	} else {
   		alert("Please enter a tag to search for!");
   		return;
   	}
   });
});