$(document).ready(function() {


   setIcons();

	/**
	* When clicked, it creates a group through the UI.
	*/
	$("#create_group").click(function(e) {
		e.preventDefault();

		var groupName = $("#group_name").val();

		if (groupName.length == 0 || !groupName) {
			return alert("Please enter in a valid group name!");
		}

		var relURL = "";

		//URL to post to
		if (location.pathname.split('/').length == 4) {
			relURL = '../../add/' + groupName + '/'
		} else {
			relURL = '../add/' + groupName + '/'
		}

		//POST REQUEST to create a group through UI
		$.post(relURL, {
			"groupname": groupName,
			"username": $("#username").text()
		}, function (data) {
			if ("Error" in data) {
				alert(data['Error']);
				return;
			} else {
				alert("Group Created!");
				location.reload();
			}
		});
	});


	/**
	* When clicked, it deletes a group through the UI.
	*/
	$(".delete").click(function (e) {
		var groupInfo = $(this).attr("id").split('concat_val_buffer');
		var groupOwner = groupInfo[1];
		var groupName = groupInfo[0];
		$.post('../delete/group/', {
			"groupOwner": groupOwner,
			"groupName": groupName,
			"username": $("#username").text()
		}, function (data) {
			if ("Error" in data) {
				alert(data['Error']);
				return;
			} else {
				location.reload();
			}
		});
	});

	/**
	* When clicked, it removes a member from the group through the UI.
	*/
	$(".remove").click(function (e) {
		var groupInfo = $(this).attr("id").split('concat_val_buffer');
		var groupOwner = groupInfo[1];
		var groupName = groupInfo[0];
		//username is name of user to remove from group
		$.post('../../unsubscribe/group/', {
			"groupOwner": groupOwner,
			"groupName": groupName,
			"username": $("#username").text()
		}, function (data) {
			if ("Error" in data) {
				alert(data['Error']);
				return;
			} else {
				alert(data['Unsubscribe']);
				location.reload();
			}
		});
	});

   /**
   * Sorts all graphs that are returned.
   */
   $(".order").click(function (e) {
      setIcon($(this).children().attr('id'));
   });

   /**
   * Sets the specific icon for property. For example, clicking icon 
   * in front of graph id will change the icon to something else.
   * @param iconId ID of icon to change
   */
   function setIcon(iconId) {
     if ($("#" + iconId).attr('class') == 'glyphicon glyphicon-sort' || $("#" + iconId).attr('class') == 'glyphicon glyphicon-sort-by-alphabet-alt') {
        setOrderQuery(iconId, 'ascending');
     } else if ($("#" + iconId).attr('class') == 'glyphicon glyphicon-sort-by-alphabet') {
        setOrderQuery(iconId, 'descending');
     }
   }

   /*
   * Modifies the order query term in the URL to sort the 
   * specified attribute.
   * @param iconID ID of icon to sort attribute
   * @param sortValue value specified which way to sort attribute (ascending, descending, none)
   */
   function setOrderQuery(iconId, sortValue) {
      if (iconId == 'order_groups_icon') {
         window.location.href = updateQueryStringParameter(window.location.href, "order", "group_" + sortValue);
      } else if (iconId == 'order_owner_icon') {
         window.location.href = updateQueryStringParameter(window.location.href, "order", "owner_" + sortValue);
      }
   }

   /**
   * Updates specified value in the query.
   */
   function updateQueryStringParameter(uri, key, value) {
     var re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
     var separator = uri.indexOf('?') !== -1 ? "&" : "?";
     if (uri.match(re)) {
       return uri.replace(re, '$1' + key + "=" + value + '$2');
     }
     else {
       return uri + separator + key + "=" + value;
     }
   }

   /**
   * Gets query variables from the url.
   * @param variable variable to find in the URL
   */
   function getQueryVariable(variable)
   {
          var query = window.location.search.substring(1);
          var vars = query.split("&");
          for (var i = 0;i < vars.length; i++) {
            var pair = vars[i].split("=");
            if(pair[0] == variable){
               return pair[1];
            }
          }
          return (false);
   }

	/**
   * Sets the icons at the loading of the page.
   */
   function setIcons() {
      var orderVariable = getQueryVariable("order");

      if (orderVariable) {
         if (orderVariable == 'group_ascending') {
            $("#order_groups_icon").attr('class', 'glyphicon glyphicon-sort-by-alphabet');
         } else if (orderVariable == 'group_descending') {
            $("#order_groups_icon").attr('class', 'glyphicon glyphicon-sort-by-alphabet-alt');
         } else if (orderVariable == 'owner_ascending') {
            $("#order_owner_icon").attr('class', 'glyphicon glyphicon-sort-by-alphabet');
         } else if (orderVariable == 'owner_descending') {
            $("#order_owner_icon").attr('class', 'glyphicon glyphicon-sort-by-alphabet-alt');
         }
      }
   }
});