/**
 * Created by adb on 09/01/17.
 */

var header = {
    init: function() {
        /**
         * Upon clicking, the user makes a
         * POST request to sign-in to GS.
         */
        $("#signinBtn").click(function(e) {
            header.onSignIn(e);
        });

        $("#registerBtn").click(function(e) {
            header.onRegister(e);
        });

        header.checkNotification()
    },
    onSignIn: function(e) {
        e.preventDefault();
        var email = $("#email").val();
        var pw = $("#pw").val();

        if (!$("#email") || email.length == 0) {
            $.notify({
                message: 'Please enter email!'
            }, {
                type: 'warning'
            });
            return;
        }

        if (!$("#pw") || pw.length == 0) {
            $.notify({
                message: 'Please enter password!'
            }, {
                type: 'warning'
            });
            return;
        }

        //POST Request to log in user
        jsonRequest('POST', "/login/", {
                "user_id": email,
                "pw": pw
            },
            successCallback = function(response) {
                window.location.reload();
            },
            errorCallback = function(response) {
                $.notify({
                    message: response.responseJSON.error_message
                }, {
                    type: 'danger'
                });
            });
    },
    onRegister: function(e) {
        e.preventDefault();
        e.preventDefault();
        var user_id = $("#user_id").val();
        var password = $("#password").val();
        var verify_password = $("#verify_password").val();

        if (!$("#user_id") || user_id.length == 0) {
            $.notify({
                message: 'Please enter your email!'
            }, {
                type: 'warning'
            });
            return;
        }

        if (!$("#password") || password.length == 0) {
            $.notify({
                message: 'Please enter a password for the account!'
            }, {
                type: 'warning'
            });
            return;
        }

        if (!$("#verify_password") || verify_password.length == 0) {
            $.notify({
                message: 'Please re-enter your password!'
            }, {
                type: 'warning'
            });
            return;
        }

        if (password !== verify_password) {
            $.notify({
                message: "Passwords do not match!"
            }, {
                type: 'warning'
            });
            return;
        }


        //POST Request to log in user
        jsonRequest('POST', "/register/", {
                "user_id": user_id,
                "password": password
            },
            successCallback = function(response) {
                window.location.reload();
            },
            errorCallback = function(response) {
                $.notify({
                    message: response.responseJSON.error_message
                }, {
                    type: 'danger'
                });
            });
    },
    checkNotification: function() {
        var user_id = $('#UserEmail').val();
        //GET Request to get number of unread notifications
        jsonRequest('GET', "/notifications/count", {
                "owner_email": user_id,
                "is_read": false
            },
            successCallback = function(response) {
                if (parseInt(response.count) > 0) {
                    $(".notification-indicator .mail-status.unread").css({ "display": "inline-block" })
                } else {
                    $(".notification-indicator .mail-status.unread").css({ "display": "none" })
                }
            },
            errorCallback = function(response) {
                $(".notification-indicator .mail-status.unread").css({ "display": "none" })
            });
    }
};

var userSocket = {
    init: function() {
        var socket = new WebSocket('ws://' + window.location.host);

        socket.onopen = userSocket.onopen

        socket.onmessage = userSocket.onmessage

        if (socket.readyState == WebSocket.OPEN) {
            socket.onopen();
        }
    },
    onopen: function() {
        console.log('Websockets connected')
    },
    onmessage: function(message) {
        data = JSON.parse(message.data)
        //$.notify({message: data.message}, {type: 'info'})
        //alert(message.data);
        // Different types of communication over sockets
        switch (data.type) {
            case "notification":
                userSocket.notification(data.message);
                break;
        }
    },
    // Socket communication for notifications
    notification: function(data) {
        $(".notification-indicator .mail-status.unread").css({ "display": "inline-block" })
        data['is_bulk'] = false
        switch (data.topic) {
            case "owner":
                $('#unread-owner-notification-table').bootstrapTable('insertRow', {
                    index: 1,
                    row: data
                });
                $("#owner-notification-total").text(parseInt($("#owner-notification-total").text()) + 1)
                break;
            case "group":
                table_name = '#group-table-false-' + data['group_id']
                if ($(table_name).length > 0) {
                    refresh_tabs = false;
                    $(table_name).bootstrapTable('insertRow', {
                        index: 1,
                        row: data
                    });
                }
                if (typeof notificationsPage !== 'undefined') {
                    notificationsPage.groupNotificationsTable.notificationsGroupCount(
                        is_read = false,
                        total_val_id = '#unread-group-notification-total',
                        table_div_id = '#unread-group-notification-tables',
                        refresh_tabs = refresh_tabs)
                }
                break;
        }
    },
}