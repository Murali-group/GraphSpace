$(document).ready(function () {
    /**
     * Mark notification as read through the UI.
     */

    $(".read_notification").click(function(e){
        var uid = $(this).attr('uid');
        // notification id present if clicked on individual notification
        var notification_ids = [$(this).attr('notification_id')];

         read_notifications(uid, notification_ids, function(error, data){
            if (error) {
                return alert(error);
            } else {
                window.location.reload();
                //$('.remove_read'+nid).remove();
                //$('.notification_event'+nid).addClass('notification_read');
            }
        });
    });

    $(".read_all_group_notifications").click(function(e){
        var uid = $(this).attr('uid');
        var group_id = $(this).attr('group_id');
        // notification id present if clicked on individual notification
        var notification_ids = [];
        $.each($('.notifications.' + group_id), function( index, notification ) {
           notification_ids.push($(notification).attr('id'));
        });

        read_notifications(uid, notification_ids, function(error, data){
            if (error) {
                return alert(error);
            } else {
                window.location.reload();
                //$('.remove_read'+nid).remove();
                //$('.notification_event'+nid).addClass('notification_read');
            }
        });
    });

    $(".read_all_notifications").click(function(e){
        var uid = $(this).attr('uid');
        var group_id = $(this).attr('group_id');
        // notification id present if clicked on individual notification
        var notification_ids = [];
        $.each($('.notifications'), function( index, notification ) {
           notification_ids.push($(notification).attr('id'));
        });

        read_notifications(uid, notification_ids, function(error, data){
            if (error) {
                return alert(error);
            } else {
                window.location.reload();
                //$('.remove_read'+nid).remove();
                //$('.notification_event'+nid).addClass('notification_read');
            }
        });
    });

    var read_notifications = function(uid, notification_ids, callback) {
        $.post('/javascript/' + uid + '/mark_notifications_as_read/', {
            'notification_ids': notification_ids
        }, function (data) {
            if (data.Error) {
                callback(data.Error, null);
            } else {
                callback(null, data);
            }
        });
    };

    $('[data-toggle="tooltip"]').tooltip();

});