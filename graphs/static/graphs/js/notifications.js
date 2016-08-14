$(document).ready(function() {
   /**
   * Mark notification as read through the UI.
   */
   $(".read_notification").click(function (e) {
    // current user_id always present
    var uid = $(this).attr('uid');
    // notification id present if clicked on individual notification
    var nid = $(this).attr('nid');
    // group id present if clicked on mark read for group notifications
    var gid = $(this).attr('gid');
    // allid present if clicked on mark all notification read for a user
    var allid = $(this).attr('allid');

    console.log(uid);
    console.log(gid);
    console.log(nid);
    console.log(allid);
    // send a post request to the view read_notification
    $.post('../../../javascript/'+uid+'/mark_notifications_as_read/', {
      'uid': uid,
      'nid': nid,
      'gid': gid,
      'allid': allid

    }, function (data) {
      if (data.Error) {
        return alert(data.Error);
      }
      window.location.reload();
    });

   });

   $('[data-toggle="tooltip"]').tooltip(); 

});