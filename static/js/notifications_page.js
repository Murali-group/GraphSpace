/**
 * Created by adb on 02/11/16.
 */


var apis = {
    notifications: {
        ENDPOINT: '/ajax/notifications/',
        get: function (data, uri, successCallback, errorCallback) {
            url = apis.notifications.ENDPOINT
            if(uri != null){
                url = url + uri
            }
            apis.jsonRequest('GET', url, data, successCallback, errorCallback)
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

        // Get group notification on click
        $('#all-group-notification').click(function(){
            notificationsPage.groupNotificationsTable.notificationsGroupCount(null, '#all-group-notification-total', '#all-group-notification-tables')
        })
        $('#unread-group-notification').click(function(){
            notificationsPage.groupNotificationsTable.notificationsGroupCount(false, '#unread-group-notification-total', '#unread-group-notification-tables')
        })

        notificationsPage.groupNotificationsTable.notificationsGroupCount(false, '#unread-group-notification-total', '#unread-group-notification-tables')

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
        }
    },
    ownerNotificationsTable:{
        unreadNotificationQuery: function(){
            /**
             * This is the custom ajaxOptions function used to load parameters for unread notification ajax request.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search.
             */
            return {
                  options: {
                    type: 'owner',
                    totalIdName: '#unread-owner-notification-total',
                    tableIdName: '#unread-owner-notification-table',
                    is_read: false
                  }
               }
        },
        allNotificationQuery: function(params){
            /**
             * This is the custom ajaxOptions function used to load parameters for all notification ajax requests.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search.
             */
            return {
                options: {
                    type: 'owner',
                    totalIdName: '#all-owner-notification-total',
                    tableIdName: '#all-owner-notification-table'
                }
            }
        },
        getNotifications: function (params) {
            /**
             * This is the custom ajax request used to load notifications.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search.
             */
            $(params.options["tableIdName"]).bootstrapTable('showLoading');
            $(params.options["totalIdName"]).html('<i class="fa fa-refresh fa-spin fa fa-fw"></i>');

            params.data["owner_email"] = $('#UserEmail').val();
            params.data["type"] = params.options["type"]
            params.data["is_read"] = params.options["is_read"]

            apis.notifications.get(params.data,
                uri = null,
                successCallback = function (response) {
                    // This method is called when notifications are successfully fetched.
                    $(params.options["tableIdName"]).bootstrapTable('hideLoading');
                    params.success(response);
                    $(params.options["totalIdName"]).text(response.total);
                },
                errorCallback = function () {
                    // This method is called when  error occurs while fetching notifications.
                    params.error('Error');
                }
            );
        },
    },
    groupNotificationsTable:{
        getNotifications: function (params) {
            /**
             * This is the custom ajax request used to load group notifications.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search.
             */

            $(params.options["tableIdName"]).bootstrapTable('showLoading');

            params.data["owner_email"] = $('#UserEmail').val();
            params.data["group_id"] = params.options["group_id"]
            params.data["type"] = params.options["type"]
            params.data["is_read"] = params.options["is_read"]

            apis.notifications.get(params.data,
                uri = null,
                successCallback = function (response) {
                    // This method is called when notifications are successfully fetched.
                    $(params.options["tableIdName"]).bootstrapTable('hideLoading');
                    params.success(response);
                },
                errorCallback = function () {
                    // This method is called when  error occurs while fetching notifications.
                    params.error('Error');
                }
            );
        },
        notificationsGroupCount: function(is_read, total_val_id, table_div_id){
            // Get list of groups in group notification
            data = {
                'member_email': $('#UserEmail').val()
            }
            options = {
                type: 'group'
            }
            if(is_read != null){
                data["is_read"] = is_read
                options["is_read"] = is_read
            }
            apis.notifications.get(
                data = data,
                uri = 'group-count',
                successCallback = function (response) {
                    // This method is called when notifications are successfully fetched.
                    var glist = $('ul.group-tabs')
                    var gtable = $(table_div_id)
                    glist.empty()
                    gtable.empty()
                    $(total_val_id).text(response.total);

                    $.each(response.groups, function(i){
                        var li = $('<li/>')
                                .appendTo(glist)
                        var a = $('<a/>')
                                .attr('href','#group-table-' + is_read + '-' + response.groups[i]['group']['id'])
                                .text(response.groups[i]['group']['name'])
                                .appendTo(li)
                        var span = $('<span/>')
                                .addClass('badge')
                                .text(response.groups[i]['count'])
                                .appendTo(a)

                        var table = $('<table/>')
                                    .attr('id','group-table-' + is_read + '-' + response.groups[i]['group']['id'])
                                    .attr('data-toggle','table')
                                    .addClass('table-no-bordered')
                                    .appendTo(gtable)

                        var br = $('<br/>')
                                .appendTo(gtable)

                        options["group_id"] = response.groups[i]['group']['id']
                        options["tableIdName"] = '#group-table-' + response.groups[i]['group']['id']

                        table.bootstrapTable({
                            ajax: notificationsPage.groupNotificationsTable.getNotifications,
                            ajaxOptions: {
                                options: options
                            },
                            sidePagination: 'server',
                            pagination: true,
                            dataField: 'notifications',
                            sortName: 'created_at',
                            sortOrder: 'desc',
                            columns:[
                                {
                                    field: 'message',
                                    title: response.groups[i]['group']['name'],
                                    valign: 'center',
                                    formatter: notificationsPage.notificationsTable.messageFormatter,
                                    events: notificationsPage.notificationsTable.operationEvents
                                },
                                {
                                    field: 'created_at',
                                    valign: 'center',
                                    align: 'center',
                                    formatter: utils.dateFormatter,
                                },
                                {
                                    field: 'operations',
                                    valign: 'center',
                                    align: 'right',
                                    formatter: notificationsPage.notificationsTable.operationsFormatter,
                                    events: notificationsPage.notificationsTable.operationEvents
                                }
                            ]
                        }) 
                    })
                },
                errorCallback = function () {
                    // This method is called when  error occurs while updating reads.
                    $.notify({message: 'Error'}, {type: 'danger'});
                }
            );
        }
    }
};