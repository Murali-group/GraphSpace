$(document).ready(function() {


   /**
   * Mark notification as read through the UI.
   */
   $(".read_notification").click(function (e) {
    var uid = $(this).val();
    var nid = $(this).attr('id');

    $.post('../../../read_notification/', {
      'uid': uid,
      'nid': nid
    }, function (data) {
      if (data.Error) {
        return alert(data.Error);
      }
      $("#read_notification").load("notifications.html #read_notification")
      // window.location.reload();
    });

   });

   /**
   * Mark all notifications as read in a group
   */
   $(".read_all_notifications").click(function (e) {
    var uid = $(this).val();
    var nid = $(this).attr('id');

    $.post('../../../read_all_notifications/', {
      'uid': uid,
      'nid': nid
    }, function (data) {
      if (data.Error) {
        return alert(data.Error);
      }
      window.location.reload();
    });
   });

  /**
   * Mark all notifications as read in a group
   */
   $(".read_all_user_notifications").click(function (e) {
    var uid = $(this).val();

    $.post('../../../read_all_user_notifications/', {
      'uid': uid
    }, function (data) {
      if (data.Error) {
        return alert(data.Error);
      }
      window.location.reload();
    });
   });

});