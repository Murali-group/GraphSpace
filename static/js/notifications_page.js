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
        read: function(id, data, successCallback, errorCallback){
            url = apis.notifications.ENDPOINT + 'read/'
            if(id != null){
                url = url + id
            }
            apis.jsonRequest('PUT', url, data, successCallback, errorCallback)
        }
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

        $('#owner-mark-all-read').click(function(){
            data = {
                owner_email: $('#UserEmail').val(),
                type: 'owner'
            }
            apis.notifications.read(
                id = null,
                data = data,
                successCallback = function (response) {
                    // This method is called when notifications are successfully fetched.
                    $('#unread-owner-notification-table').bootstrapTable('refresh')
                    $('#all-owner-notification-table').bootstrapTable('refresh')
                    $.notify({message: response.message}, {type: 'success'});
                },
                errorCallback = function () {
                    // This method is called when  error occurs while updating reads.
                    $.notify({message: 'Error'}, {type: 'danger'});
                }
            );
        })

        utils.initializeTabs();
    },
    notificationsTable: {
        messageFormatter: function (value, row, index) {
            return $('<a>').attr('href', '/notification/' + row.id + '/redirect/?owner_email=' + $('#UserEmail').val() + '&type=owner').text(row.message)[0].outerHTML;
        },
        operationsFormatter: function (value, row, index) {
            if (!row.is_read){
                return [
                    '<a class="mark-as-read" href="javascript:void(0)" title="Mark as read">',
                    '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>',
                    '</a>'
                ].join('');
            }
            return '' 
        },
        operationEvents: {
            'click .mark-as-read': function (e, value, row, index) {
                // Mark as read
                data = {
                    owner_email: $('#UserEmail').val(),
                    type: 'owner'
                }
                apis.notifications.read(
                    id = row['id'],
                    data = data,
                    successCallback = function (response) {
                        // This method is called when notifications are successfully fetched.
                        $('#all-owner-notification-table').bootstrapTable('refresh')
                        $.notify({message: response.message}, {type: 'success'});
                        $('#unread-owner-notification-table').bootstrapTable('remove', {
                            field: 'id',
                            values: [row['id']]
                        });
                    },
                    errorCallback = function () {
                        // This method is called when  error occurs while updating reads.
                        $.notify({message: 'Error'}, {type: 'danger'});
                    }
                );
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
            params["totalIdName"] = '#unread-owner-notification-total';
            params["tableIdName"] = '#unread-owner-notification-table';
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
            params["totalIdName"] = '#all-owner-notification-total';
            params["tableIdName"] = '#all-owner-notification-table';
            return params
        }
    }
};