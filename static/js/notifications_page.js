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
        nameFormatter: function (value, row) {
            return $('<a>').attr('href', location.pathname + row.id).text(row.name)[0].outerHTML;
        },
        operationsFormatter: function (value, row, index) {
            return [
                '<a class="mark-as-read btn btn-default btn-sm" href="javascript:void(0)" title="Mark as read">',
                'Mark as read</i>',
                '</a>'
            ].join('');
        },
        operationEvents: {
            'click .mark-as-read': function (e, value, row, index) {
                // Mark as read
            }
        },
        getAllNotifications: function (params) {
            /**
             * This is the custom ajax request used to load notifications in notificationsTable.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search.
             */

            if (params.data["search"]) {
                // Currently we assume that term entered in the search bar is used to search for the group name only.
                params.data["name"] = '%' + params.data["search"] + '%';
            }
            params.data["owner_email"] = $('#UserEmail').val();

            apis.notifications.get(params.data,
                successCallback = function (response) {
                    // This method is called when notifications are successfully fetched.
                    params.success(response);
                    $('#ownedGroupsTotal').text(response.total);
                },
                errorCallback = function () {
                    // This method is called when  error occurs while fetching notifications.
                    params.error('Error');
                }
            );
        }
    }
};
