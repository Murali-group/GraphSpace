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
          if(data.Message == 'User added!') {
              location.reload();          
            } else {
              return alert(data.Message);
          }
      });
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
            if(data.Message == 'User removed from group!') {
              location.reload();          
            } else {
              return alert(data.Message);
            }
        }   
      });
   });

});