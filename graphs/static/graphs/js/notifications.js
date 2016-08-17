$(document).ready(function () {
    /**
     * Mark notification as read through the UI.
     */


    // Method to mark as read individual notifications
    $(".read_notification").click(function(e){
        // get the user id of the logged in user
        var uid = $(this).attr('uid');
        // get a list of notification ids, in this case it will be a
        // list of length 1 as it a single notification
        var notification_ids = [$(this).attr('notification_id')];
        // Call function read_notification which sends a POST request to mark
        // notification as read
         read_notifications(uid, notification_ids, function(error, data){
            if (error) {
                return alert(error);
            } else {
                // If no error is caught that manipulate the DOM for notification
                manipulate_dom(notification_ids);
            }
        });
    });

    // Method to mark all notification of a group as read for the user
    $(".read_all_group_notifications").click(function(e){
        // get the user id of the logged in user
        var uid = $(this).attr('uid');
        // get the group id of the notifications that need to be marked as read
        var group_id = $(this).attr('group_id');
        // create a list of notification ids which are present in the group
        var notification_ids = [];
        $.each($('.notifications.' + group_id), function( index, notification ) {
           notification_ids.push($(notification).attr('id'));
        });
        // Call function read_notifications which sends a POST request to mark
        // notifications as read
        read_notifications(uid, notification_ids, function(error, data){
            if (error) {
                return alert(error);
            } else {
                // If no error is caught that manipulate the DOM for notification
                manipulate_dom(notification_ids);
            }
        });
    });

    // Method to mark all notifications as read for the user
    $(".read_all_notifications").click(function(e){
        // get the user id of the logged in user
        var uid = $(this).attr('uid');
        // create a list of notification ids which are present in the group
        var notification_ids = [];
        $.each($('.notifications'), function( index, notification ) {
           notification_ids.push($(notification).attr('id'));
        });
        // Call function read_notification which sends a POST request to mark
        // notifications as read
        read_notifications(uid, notification_ids, function(error, data){
            if (error) {
                return alert(error);
            } else {
                // If no error is caught that manipulate the DOM for notification
                manipulate_dom(notification_ids);
                $
            }
        });
    });

    // send a POST request to the view method mark_notificartions_as_read_api
    // with a list of notification_ids
    var read_notifications = function(uid, notification_ids, callback) {
        console.log(notification_ids);
        $.post('/javascript/' + uid + '/mark_notifications_as_read_api/', {
            'notification_ids[]': [notification_ids]
        }, function (data) {
            if (data.Error) {
                callback(data.Error, null);
            } else {
                callback(null, data);
            }
        });
    };

    // grey out notification row and remove the tick mark for notification row
    var manipulate_dom = function(notification_ids){
        $.each($(notification_ids), function(index, element){
            $('.remove_read'+element).remove();
            $('.notification_event'+element).addClass('notification_read');
         });
    };

    // helper function for tooltip, used to display text when cursors hovers on
    // the read tick marks.
    $('[data-toggle="tooltip"]').tooltip();
});