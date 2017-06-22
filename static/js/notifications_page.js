/**
 * Created by adb on 02/11/16.
 */


var apis = {
    notifications: {
        ENDPOINT: '/ajax/notifications/',
        get: function (data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.notifications.ENDPOINT, data, successCallback, errorCallback)
        },
        update: function (id, data, successCallback, errorCallback) {
            apis.jsonRequest('PUT', apis.notifications.ENDPOINT + id, data, successCallback, errorCallback)
        },
    },
    jsonRequest: function (method, url, data, successCallback, errorCallback) {
        $.ajax({
            headers: {
                'Accept': 'application/json'
            },
            method: method,
            data: data,
            url: url,
            success: successCallback,
            error: errorCallback
        });
    }

};

var notificationsPage = {
    init: function () {
        /**
         * This function is called to setup the notifications page.
         * It will initialize all the event listeners.
         */
        console.log('Loading Notifications Page....');

        utils.initializeTabs();
    },
    notificationsTable: {
        messageFormatter: function (value, row, index) {
            return $('<a>').attr('href', '/'+ row.resource + '/' + row.resource_id).text(row.message)[0].outerHTML;
        },
        operationsFormatter: function (value, row, index) {
            return [
                '<a class="mark-as-read" href="javascript:void(0)" title="Mark as read">',
                '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>',
                '</a>'
            ].join('');
        },
        operationEvents: {
            'click .mark-as-read': function (e, value, row, index) {
                // Mark as read
            }
        },
        getNotifications: function (params) {
            /**
             * This is the custom ajax request used to load notifications.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search.
             */
            $(params.data["tableIdName"]).bootstrapTable('showLoading');
            $(params.data["totalIdName"]).html('<i class="fa fa-refresh fa-spin fa fa-fw"></i>');
            params.data["owner_email"] = $('#UserEmail').val();

            apis.notifications.get(params.data,
                successCallback = function (response) {
                    // This method is called when notifications are successfully fetched.
                    $(params.data["tableIdName"]).bootstrapTable('hideLoading');
                    params.success(response);
                    $(params.data["totalIdName"]).text(response.total);
                },
                errorCallback = function () {
                    // This method is called when  error occurs while fetching notifications.
                    params.error('Error');
                }
            );
        },
    },
    ownerNotificationsTable:{
        unreadNotificationQuery: function(params){
            /**
             * This is the custom query params function used to load parameters for unread notification ajax request.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search.
             */
            params["type"] = 'owner';
            params["totalIdName"] = '#unreadOwnerNotificationTotal';
            params["tableIdName"] = '#unreadOwnerNotificationTable';
            params["is_read"] = false;
            return params
        },
        allNotificationQuery: function(params){
            /**
             * This is the custom query params function used to load parameters for all notification ajax requests.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search.
             */
            params["type"] = 'owner';
            params["totalIdName"] = '#allOwnerNotificationTotal';
            params["tableIdName"] = '#allOwnerNotificationTable';
            return params
        }
    }
};
