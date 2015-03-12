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

   $("#change_desc").click(function(e) {
    e.preventDefault();

    var desc = $("#desc").val();

    var username = $("#username").text();

    var groupId= $("#groupId").text();

    var groupOwner = $("#groupOwner").text();

    $.post("../../changeDescription/", {
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

   $("#add_member").click(function(e) {
    e.preventDefault();

    var member = $("#member_name").val();

    var groupId= $("#groupId").text();

    var groupOwner = $("#groupOwner").text();

    if (member.length == 0 || member == null) {
      return alert("Please enter email of user to add to this group!");
    }

    $.post("../../addMember/", {
        "member": member,
        "groupId": groupId,
        "groupOwner": groupOwner
      }, function (data) {
          if (data.Message) {
            alert(data.Message);
            location.reload();          
        }   
      });
   });

});