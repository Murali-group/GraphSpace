/**
 * Created by adb on 09/01/17.
 */

var header = {
    init: function () {
        /**
         * Upon clicking, the user makes a
         * POST request to sign-in to GS.
         */
        $("#signinBtn").click(function (e) {
            header.onSignIn(e);
        });

        $("#registerBtn").click(function (e) {
            header.onRegister(e);
        });
    },
    onSignIn: function (e) {
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
            successCallback = function (response) {
                window.location.reload();
            },
            errorCallback = function (response) {
                $.notify({
                    message: response.responseJSON.error_message
                }, {
                    type: 'danger'
                });
            });
    },
    onRegister: function (e) {
        e.preventDefault();
        e.preventDefault();
        var user_id = $("#user_id").val();
        var password = $("#password").val();
        var verify_password = $("#verify_password").val();

        if ($("#user_id")) {
            var reg = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
            if (reg.test(user_id) == false) {
                $.notify({
                message: 'Please enter a valid email address!'
                }, {
                    type: 'warning'
                });
                return;
            }
        }

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
            successCallback = function (response) {
                window.location.reload();
            },
            errorCallback = function (response) {
                $.notify({
                    message: response.responseJSON.error_message
                }, {
                    type: 'danger'
                });
            });
    }
};