$(document).ready(function() {



    //these accordions make up the side menu
    //and set it to the minimum value when page is viewed
   $('#accordion_description').accordion({
      collapsible: true
    });

   $('#accordion_owner').accordion({
      collapsible: true,
   });

   $('#accordion_members').accordion({
      collapsible: true,
   });

   $('#accordion_tags').accordion({
      collapsible: true,
   });

   if (getQueryVariable('search')) {
    $("#searching").val(decodeURIComponent(getQueryVariable('search')));
   }

   if (getQueryVariable('tags')) {
    $("#tags_searching").val(decodeURIComponent(getQueryVariable('tags')));
   } 

   /**
   * When clicked, it replaces the description of the current
   * group with the description user entered through the UI
   */
   $("#change_desc").click(function(e) {
    e.preventDefault();

    var desc = $("#desc").val();

    var username = $("#username").text();

    var groupId= $("#groupId").text();

    var groupOwner = $("#groupOwner").text();

    //POST REQUEST to change description of group
    $.post("../../../changeDescription/", {
        "description": desc,
        "username": username,
        "groupId": groupId,
        "groupOwner": groupOwner
      }, function (data) {
          if (data.Error) {
            alert(data.Error);
            return;
          }
          location.reload();
      });
   });

   /**
   * When clicked, it adds a member (current GS user)
   * to current group.  MUST BE GROUP OWNER TO DO THIS.
   */
   $("#add_member").click(function(e) {
    e.preventDefault();

    var member = $("#member_name").val();

    var groupId= $("#groupId").text();

    var groupOwner = $("#groupOwner").text();

    if (member.length == 0 || member == null) {
      return alert("Please enter email of user to add to this group!");
    }

    //POST REQUEST to add member to group
    $.post("../../../addMember/", {
        "member": member,
        "groupId": groupId,
        "groupOwner": groupOwner
      }, function (data) {
        console.log(data);
          if(data.Message == 'Become the owner/member of this group first!') {
              return alert(data.Message);
            } else {
              location.reload();          
          }
      });
   });

   $("#clear_search").click(function(e) {
    e.preventDefault();
    location.href = document.URL;
   });

   /**
   * When clicked, it removes a member (current GS user)
   * from current group.  MUST BE GROUP OWNER TO DO THIS.
   */
   $(".removeMember").click(function(e) {
    e.preventDefault();

    var member = $(this).attr('id');

    var groupId= $("#groupId").text();

    var groupOwner = $("#groupOwner").text();
    
    //POST REQUEST to remove member from group
    $.post("../../../removeMember/", {
        "member": member,
        "groupId": groupId,
        "groupOwner": groupOwner
      }, function (data) {
          if (data.Message) {
            if(data.Message == "Can't delete user from a group you are not the owner of!") {
              return alert(data.Message);
            } else {
              location.reload();
            }
        }   
      });
   });


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

});