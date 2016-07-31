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
      window.location.reload();
    });
   });
});