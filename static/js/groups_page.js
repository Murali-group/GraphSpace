/**
 * Created by adb on 02/11/16.
 */


var apis = {
    groups: {
        ENDPOINT: '/ajax/groups/',
        get: function (data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.groups.ENDPOINT, data, successCallback, errorCallback)
        },
        add: function (data, successCallback, errorCallback) {
            apis.jsonRequest('POST', apis.groups.ENDPOINT, data, successCallback, errorCallback)
        },
        getByID: function (id, data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.groups.ENDPOINT + id, undefined, successCallback, errorCallback)
        },
        update: function (id, data, successCallback, errorCallback) {
            apis.jsonRequest('PUT', apis.groups.ENDPOINT + id, data, successCallback, errorCallback)
        },
        delete: function (id, successCallback, errorCallback) {
            apis.jsonRequest('DELETE', apis.groups.ENDPOINT + id, undefined, successCallback, errorCallback)
        },
        getSharedGraphs: function (id, data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.groups.ENDPOINT + id + '/graphs', data, successCallback, errorCallback)
        },
        shareGraph: function (id, data, successCallback, errorCallback) {
            apis.jsonRequest('POST', apis.groups.ENDPOINT + id + '/graphs', data, successCallback, errorCallback)
        },
        unshareGraph: function (group_id, graph_id, successCallback, errorCallback) {
            apis.jsonRequest('DELETE', apis.groups.ENDPOINT + group_id + '/graphs/' + graph_id, undefined, successCallback, errorCallback)
        },
        getMembers: function (group_id, data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.groups.ENDPOINT + group_id + '/members', data, successCallback, errorCallback)
        },
        addMember: function (group_id, data, successCallback, errorCallback) {
            apis.jsonRequest('POST', apis.groups.ENDPOINT + group_id + '/members', data, successCallback, errorCallback)
        },
        deleteMember: function (group_id, member_id, successCallback, errorCallback) {
            apis.jsonRequest('DELETE', apis.groups.ENDPOINT + group_id + '/members/' + member_id, undefined, successCallback, errorCallback)
        }
    },
    discussion: {
        ENDPOINT: '/ajax/groups/',
        addDiscussion: function (id, data, successCallback, errorCallback) {
            apis.jsonRequest('POST', apis.groups.ENDPOINT + id + '/discussions', data, successCallback, errorCallback)
        },
        getSharedDiscussions: function (id, data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.groups.ENDPOINT + id + '/discussions', data, successCallback, errorCallback)
        },
        getComments: function (group_id, discussion_id, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.groups.ENDPOINT + group_id + '/discussions/' + discussion_id, undefined, successCallback, errorCallback)
        },
        deleteDiscussion: function (group_id, data, successCallback, errorCallback) {
            apis.jsonRequest('DELETE', apis.groups.ENDPOINT + group_id + '/discussions', data, successCallback, errorCallback)
        },
        editDiscussion: function (group_id, data, successCallback, errorCallback) {
            apis.jsonRequest('PUT', apis.groups.ENDPOINT + group_id + '/discussions', data, successCallback, errorCallback)
        },
        addComment: function (group_id, discussion_id, data, successCallback, errorCallback) {
            apis.jsonRequest('POST', apis.groups.ENDPOINT + group_id + '/discussions/' + discussion_id, data, successCallback, errorCallback)
        },
        editComment: function (group_id, discussion_id, data, successCallback, errorCallback) {
            apis.jsonRequest('PUT', apis.groups.ENDPOINT + group_id + '/discussions/' + discussion_id, data, successCallback, errorCallback)
        },
        deleteComment: function (group_id, discussion_id, data, successCallback, errorCallback) {
            apis.jsonRequest('DELETE', apis.groups.ENDPOINT + group_id + '/discussions/' + discussion_id, data, successCallback, errorCallback)
        },
        addCommentReaction: function (group_id, discussion_id, comment_id, data, successCallback, errorCallback) {
            apis.jsonRequest('POST', apis.groups.ENDPOINT + group_id + '/discussions/' + discussion_id + '/' + comment_id, data, successCallback, errorCallback)
        },
        deleteCommentReaction: function (group_id, discussion_id, comment_id, data, successCallback, errorCallback) {
            apis.jsonRequest('DELETE', apis.groups.ENDPOINT + group_id + '/discussions/' + discussion_id + '/' + comment_id, data, successCallback, errorCallback)
        },
        getCommentReaction: function (group_id, discussion_id, comment_id, data, successCallback, errorCallback) {
            apis.jsonRequest('Get', apis.groups.ENDPOINT + group_id + '/discussions/' + discussion_id + '/' + comment_id, data, successCallback, errorCallback)
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

var groupsPage = {
    init: function () {
        /**
         * This function is called to setup the groups page.
         * It will initialize all the event listeners.
         */
        console.log('Loading Groups Page....');
        $('#CreateGroupBtn').click(groupsPage.createGroupForm.submit);

        utils.initializeTabs();

        $('#ConfirmDeleteGroupBtn').click(groupsPage.groupsTable.onDeleteGroupConfirm);
    },
    createGroupForm: {
        submit: function (e) {
            e.preventDefault();

             $('#CreateGroupBtn').attr('disabled', true);

            var group = {
                "name": $("#GroupNameInput").val() == "" ? undefined : $("#GroupNameInput").val(),
                "description": $("#GroupDescriptionInput").val() == "" ? undefined : $("#GroupDescriptionInput").val(),
                "owner_email": $('#UserEmail').val()
            };

            if (!group['name']) {
                $('#CreateGroupBtn').attr('disabled', false);
                $.notify({
                    message: 'Please enter in a valid group name!'
                }, {
                    type: 'warning'
                });
                return;
            }

            apis.groups.add(group,
                successCallback = function (response) {
                    // This method is called when group is successfully added.
                    window.location = location.pathname;
                },
                errorCallback = function (xhr, status, errorThrown) {
                    // This method is called when  error occurs while adding group.
                    if(xhr.responseJSON.error_message.includes('duplicate key')) {
                        $.notify({
                            message: 'Group name ' + group['name'] + ' already exists!'
                        }, {
                            type: 'danger'
                        });
                    }
                    else {
                        $.notify({
                            message: xhr.responseText
                        }, {
                            type: 'danger'
                        });
                    }
                    $('#CreateGroupBtn').attr('disabled', false);
                });
        }
    },
    groupsTable: {
        nameFormatter: function (value, row) {
            return $('<a>').attr('href', location.pathname + row.id).text(row.name)[0].outerHTML;
        },
        operationsFormatter: function (value, row, index) {
            return [
                '<a class="remove btn btn-default btn-sm" href="javascript:void(0)" title="Remove">',
                'Remove <i class="glyphicon glyphicon-trash"></i>',
                '</a>'
            ].join('');
        },
        operationEvents: {
            'click .remove': function (e, value, row, index) {
                $('#deleteGroupModal').data('id', row.id).data('tableId', $(e.target).closest('table').attr('id')).modal('show');
            }
        },
        onDeleteGroupConfirm: function (e) {
            e.preventDefault();
            apis.groups.delete($('#deleteGroupModal').data('id'),
                successCallback = function (response) {
                    // This method is called when group is successfully deleted.
                    // The entry from the table is deleted.
                    $('#' + $('#deleteGroupModal').data('tableId')).bootstrapTable('remove', {
                        field: 'id',
                        values: [$('#deleteGroupModal').data('id')]
                    });
                    $('#deleteGroupModal').modal('hide');
                },
                errorCallback = function (xhr, status, errorThrown) {
                    // This method is called when  error occurs while deleting group.
                    alert(xhr.responseText);
                });
        }
    },
    ownedGroupsTable: {
        getGroupsByOwner: function (params) {
            /**
             * This is the custom ajax request used to load groups in ownedGroupsTable.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search, sort, order.
             */

            if (params.data["search"]) {
                // Currently we assume that term entered in the search bar is used to search for the group name only.
                params.data["name"] = '%' + params.data["search"] + '%';
            }
            params.data["owner_email"] = $('#UserEmail').val();

            apis.groups.get(params.data,
                successCallback = function (response) {
                    // This method is called when groups are successfully fetched.
                    params.success(response);
                    $('#ownedGroupsTotal').text(response.total);
                },
                errorCallback = function () {
                    // This method is called when  error occurs while fetching groups.
                    params.error('Error');
                }
            );
        }
    },
    memberGroupsTable: {
        getGroupsByMember: function (params) {
            /**
             * This is the custom ajax request used to load groups in memberGroupsTable.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search, sort, order.
             */

            if (params.data["search"]) {
                // Currently we assume that term entered in the search bar is used to search for the group name only.
                params.data["name"] = '%' + params.data["search"] + '%';
            }
            params.data["member_email"] = $('#UserEmail').val();

            apis.groups.get(params.data,
                successCallback = function (response) {
                    // This method is called when groups are successfully fetched.
                    params.success(response);
                    $('#memberGroupsTotal').text(response.total);
                },
                errorCallback = function () {
                    // This method is called when  error occurs while fetching groups.
                    params.error('Error');
                }
            );
        }
    }
};

var groupPage = {
    init: function () {
        /**
         * This function is called to setup the group page.
         * It will initialize all the event listeners.
         */
        console.log('Loading Group Page....');
        utils.initializeTabs();

        $('.new_group_member_email_input').select2({
            placeholder: "Enter email id.....",
            ajax: {
                url: "/ajax/users/",
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        email: '%' + params.term + '%', // search term
                        offset: 0, //params.page*30 - 30,
                        limit: 100
                    };
                },
                processResults: function (data, params) {
                    // parse the results into the format expected by Select2
                    // since we are using custom formatting functions we do not need to
                    // alter the remote JSON data, except to indicate that infinite
                    // scrolling can be used
                    params.limit = params.limit || 100;

                    return {
                        results: data.users,
                        pagination: {
                            more: (params.limit) < data.total_count
                        }
                    };
                },
                cache: true
            },
            escapeMarkup: function (markup) {
                return markup;
            }, // let our custom formatter work
            minimumInputLength: 1,
            templateResult: function (user) {
                    if (user.email) {
                        return user.email;
                    } else {
                        return user.text;
                    }
                },
            templateSelection: function (user) {
                    if (user.email) {
                        return user.email;
                    } else {
                        return user.text;
                    }
                }
        });

        $('#CreateDiscussionBtn').click(groupPage.createDiscussionForm.submit);
        $('#UpdateGroupBtn').click(groupPage.updateGroupForm.submit);
        $('#ConfirmRemoveGroupToGraphBtn').click(groupPage.SharedGraphsTable.onRemoveGroupToGraphConfirm);
        $('#ConfirmRemoveGroupToDiscussionBtn').click(groupPage.sharedDiscussionsTable.onRemoveGroupToDiscussionConfirm);
        $('#ConfirmRemoveGroupMemberBtn').click(groupPage.GroupMembersTable.onRemoveGroupMemberConfirm);
        $('#submitNewGroupMemberEmailBtn').click(groupPage.onAddGroupMember);
    },
    onAddGroupMember: function (e) {
        e.preventDefault();
        if (_.isEmpty(_.trim($('.new_group_member_email_input').val()))) {
            $.notify({
                message: 'Please enter a valid email id!'
            }, {
                type: 'warning'
            });
            return;
        }

        apis.groups.addMember($('#GroupID').val(), {
                'member_id': _.trim($('.new_group_member_email_input').val())
            },
            successCallback = function (response) {
                // This method is called when a new group member relationship is successfully added.

                $('.new_group_member_email_input').val(null).trigger("change"); // Reset Input field
                $('#GroupMembersTable').bootstrapTable('refresh');
            },
            errorCallback = function (response) {
                // This method is called when  error occurs while add group_to_user relationship.
                $('.new_group_member_email_input').val(null).trigger("change"); // Reset Input field
                $.notify({
                    message: response.responseJSON.error_message
                }, {
                    type: 'danger'
                });
            });
    },
    updateGroupForm: {
        submit: function (e) {
            e.preventDefault();

            $('#UpdateGroupBtn').attr('disabled', true);

            var group = {
                "name": $("#GroupNameInput").val() == "" ? undefined : $("#GroupNameInput").val(),
                "description": $("#GroupDescriptionInput").val() == "" ? undefined : $("#GroupDescriptionInput").val()
            };

            if (!group['name']) {
                $('#UpdateGroupBtn').attr('disabled', false);
                $.notify({
                    message: 'Please enter in a valid group name!'
                }, {
                    type: 'warning'
                });
                return
            }

            apis.groups.update($('#GroupID').val(), group,
                successCallback = function (response) {
                    // This method is called when group is successfully updated.
                    window.location = location.pathname;
                },
                errorCallback = function (xhr, status, errorThrown) {
                    // This method is called when  error occurs while updating group.
                    if(xhr.responseJSON.error_message.includes('duplicate key')) {
                        $.notify({
                            message: 'Group name ' + group['name'] + ' already exists!'
                        }, {
                            type: 'danger'
                        });
                    }
                    else {
                        $.notify({
                            message: xhr.responseText
                        }, {
                            type: 'danger'
                        });
                    }
                    $('#UpdateGroupBtn').attr('disabled', false);
                });
        }
    },
    createDiscussionForm: {
        submit: function (e) {
            e.preventDefault();

             $('#CreateDiscussionBtn').attr('disabled', true);
            var discussion = {
                "topic": $("#DiscussionTopicInput").val() == "" ? undefined : $("#DiscussionTopicInput").val(),
                "description": $("#DiscussionDescriptionInput").val() == "" ? undefined : $("#DiscussionDescriptionInput").val(),
                "owner_email": $('#UserEmail').val(),
                "group_id": $('#GroupID').val()                
            };
            if (!discussion['topic']) {
                $('#CreateDiscussionBtn').attr('disabled', false);
                $.notify({
                    message: 'Please enter in a valid topic'
                }, {
                    type: 'warning'
                });
                return;
            }

            apis.discussion.addDiscussion($('#GroupID').val(), discussion,
                successCallback = function (response) {
                    // This method is called when discussion is successfully added.

                    window.location = location.pathname + '#discussions';
                    window.location.reload()


                },
                errorCallback = function (xhr, status, errorThrown) {
                    // This method is called when  error occurs while adding discussion.
                    if(xhr.responseJSON.error_message.includes('duplicate key')) {
                        $.notify({
                            message: 'Discussion topic ' + discussion['topic'] + ' already exists!'
                        }, {
                            type: 'danger'
                        });
                    }
                    else {
                        $.notify({
                            message: xhr.responseText
                        }, {
                            type: 'danger'
                        });
                    }
                    $('#CreateDiscussionBtn').attr('disabled', false);
                });
        }
    },
    SharedGraphsTable: {
        visibilityFormatter: function (value, row) {
            if (row.is_public === 1) {
                return "<i class='fa fa-globe fa-lg'></i> Public";
            } else {
                return "<i class='fa fa-lock fa-lg'></i> Private";
            }
        },
        nameFormatter: function (value, row) {
            return $('<a>').attr('href', '/graphs/' + row.id).text(row.name)[0].outerHTML;
        },
        operationsFormatter: function (value, row, index) {
            return [
                '<a class="remove btn btn-default btn-sm" href="javascript:void(0)" title="Remove">',
                'Unshare <i class="glyphicon glyphicon-remove"></i>',
                '</a>'
            ].join('');
        },
        operationEvents: {
            'click .remove': function (e, value, row, index) {
                $('#deleteGroupToGraphModal').data('id', row.id).modal('show');
            }
        },
        onRemoveGroupToGraphConfirm: function (e) {
            e.preventDefault();
            apis.groups.unshareGraph($('#GroupID').val(), $('#deleteGroupToGraphModal').data('id'),
                successCallback = function (response) {
                    // This method is called when group_to_graph relationship is successfully deleted.
                    // The entry from the table is deleted.
                    $('#SharedGraphsTable').bootstrapTable('remove', {
                        field: 'id',
                        values: [$('#deleteGroupToGraphModal').data('id')]
                    });
                    $('#deleteGroupToGraphModal').modal('hide');
                },
                errorCallback = function (xhr, status, errorThrown) {
                    // This method is called when  error occurs while deleting group_to_graph relationship.
                    alert(xhr.responseText);
                });
        },
        getGraphsSharedToGroup: function (params) {
            /**
             * This is the custom ajax request used to load graphs in SharedGraphsTable.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search, sort, order.
             */

            if (params.data["search"]) {
                // Currently we assume that term entered in the search bar is used to search for the graph name only.
                params.data["names"] = '%' + params.data["search"] + '%';
            }

            apis.groups.getSharedGraphs($('#GroupID').val(), params.data,
                successCallback = function (response) {
                    // This method is called when groups are successfully fetched.
                    params.success(response);
                },
                errorCallback = function () {
                    // This method is called when  error occurs while fetching groups.
                    params.error('Error');
                }
            );
        }
    },
    sharedDiscussionsTable: {
        discussionFormatter: function (value, row) {
            str ='<div id="DiscussionRow' + row.id + '" >';
            str += '<div>' + groupPage.sharedDiscussionsTable.visibilityFormatter(value, row) + groupPage.sharedDiscussionsTable.nameFormatter(value, row) + groupPage.sharedDiscussionsTable.deleteFormatter(value, row) + groupPage.sharedDiscussionsTable.isClosedFormatter(value, row) + '</div>';
            str +='<div><h6><i>' + '#'+ row.id + groupPage.sharedDiscussionsTable.dateFormatter(value, row) + ' by ' + row.owner_email +  '</i></h6></div>';
            str +='</div>';
            
            return str;
        },
        visibilityFormatter: function (value, row) {
            if (row.is_closed === 1) {
                return '<i class="fa fa-lock discussion-lock' + String(row.id) + '"></i><i class="fa fa-unlock passive discussion-unlock' + String(row.id) + '"></i> ';
            } else {
                return '<i class="fa fa-unlock discussion-unlock' + String(row.id) + '"></i><i class="fa fa-lock passive discussion-lock' + String(row.id) + '"></i> ';
            }
        },
        dateFormatter: function(value, row){
            if(row.is_closed ===1){
                var str = '';
                str += '<span class="discussion-lock' + String(row.id) + '">';
                str += ' closed ';
                str += moment(row.updated_at).fromNow();
                str += '</span>';
                str += '<span class="passive discussion-unlock' + String(row.id) + '">';
                str += ' opened ';
                str += moment(row.created_at).fromNow();
                str += '</span>';
                return str;
            } else{
                var str = '';
                str += '<span class="discussion-unlock' + String(row.id) + '">';
                str += ' opened ';
                str += moment(row.created_at).fromNow();
                str += '</span>';
                str += '<span class="passive discussion-lock' + String(row.id) + '">';
                str += ' closed ';
                str += moment(row.updated_at).fromNow();
                str += '</span>';
                return str;
            }
        },
        nameFormatter: function (value, row) {
            return $('<a>').attr('href', $('#GroupID').val() +'/discussions/' + row.id).text(row.topic)[0].outerHTML;
        },
        deleteFormatter: function (value, row) {
            if(row.owner_email === $('#UserEmail').val()){
                return [
                '<a style = "float:right;"  onclick = "groupPage.sharedDiscussionsTable.operationEvents(\''+row.owner_email+'\',\''+row.id+'\')"   id="deleteModal' + String(row.id) + '" href="javascript:void(0)" title="Delete">',
                'Delete <i class="fa fa-trash"></i>&nbsp;',
                '</a>'
            ].join('');
            }
            else return '';
        },
        isClosedFormatter: function (value, row) {
            if(row.owner_email === $('#UserEmail').val()){
                if (row.is_closed === 1){
                var str = '';
                str+= '<a style = "float:right;" onclick="groupPage.sharedDiscussionsTable.closeReopenDiscussion(\''+0+'\',\''+row.id+'\')" href="javascript:void(0)" title="Reopen">';
                str+= '<span class="discussion-lock' + String(row.id) + '">Reopen</span>&nbsp;&nbsp;';
                str+= '</a>';
                str+= '<a style = "float:right;" onclick="groupPage.sharedDiscussionsTable.closeReopenDiscussion(\''+1+'\',\''+row.id+'\')" href="javascript:void(0)" title="Close">';
                str+= '<span class="passive discussion-unlock' + String(row.id) + '">Close</span>&nbsp;&nbsp;';
                str+= '</a>';
                return str;
            } else{
                var str = '';
                str+= '<a style = "float:right;" onclick="groupPage.sharedDiscussionsTable.closeReopenDiscussion(\''+1+'\',\''+row.id+'\')" href="javascript:void(0)" title="Close">';
                str+= '<span class="discussion-unlock' + String(row.id) + '">Close</span>&nbsp;&nbsp;';
                str+= '</a>';
                str+= '<a style = "float:right;" onclick="groupPage.sharedDiscussionsTable.closeReopenDiscussion(\''+0+'\',\''+row.id+'\')" href="javascript:void(0)" title="Reopen">';
                str+= '<span class="passive discussion-lock' + String(row.id) + '">Reopen</span>&nbsp;&nbsp;';
                str+= '</a>';
                return str;
            }
            } else{
                return '';
            }
            
        },
        operationEvents: function (owner_email, id) {
                if (owner_email === $('#UserEmail').val()){
                    $('#DeleteDiscussionModal').data('id', id).modal('show');
                } else{
                    $.notify({
                      message: 'You are not authorized to delete this discussion'
                  }, {
                      type: 'danger'
                  });
                }
            
        },
        closeReopenDiscussion: function(is_closed,discussion_id){
            
            var discussion = {
                "is_closed": is_closed,
                "discussion_id": discussion_id
            };

                apis.discussion.editDiscussion($('#GroupID').val(), discussion,
                successCallback = function (response) {
                },
                errorCallback = function (xhr, status, errorThrown) {
                });
        },    
        onRemoveGroupToDiscussionConfirm: function (e) {
            e.preventDefault();
            var discussion = {
                "discussion_id": $('#DeleteDiscussionModal').data('id')
            };
            apis.discussion.deleteDiscussion($('#GroupID').val(), discussion,
                successCallback = function (response) {
                    // This method is called when discussion is successfully deleted.
                    // The entry from the table is deleted.
                    $('#sharedDiscussionsTable').bootstrapTable('remove', {
                        field: 'id',
                        values: [$('#DeleteDiscussionModal').data('id')]
                    });
                    $('#DeleteDiscussionModal').modal('hide');
                    var total_discussions = $('#groupDiscussionsTotal').text() - 1;
                    $('#groupDiscussionsTotal').text(total_discussions);
                },
                errorCallback = function (xhr, status, errorThrown) {

                    // This method is called when  error occurs while deleting discussion.

                    alert(xhr.responseText);
                });
        },
        getDiscussionsSharedToGroup: function (params) {
            /**
             * This is the custom ajax request used to load discussion in sharedDiscussionsTable.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search, sort, order.
             */

            if (params.data["search"]) {
                // Currently we assume that term entered in the search bar is used to search for the discussion topic, email, comment only.
                params.data["keyword"] = '%' + params.data["search"] + '%';
            }

            apis.discussion.getSharedDiscussions($('#GroupID').val(), params.data,
                successCallback = function (response) {
                    // This method is called when discussions are successfully fetched.
                    params.success(response);
                    $('#groupDiscussionsTotal').text(response.total);
                },
                errorCallback = function () {
                    // This method is called when  error occurs while fetching discussions.
                    params.error('Error');
                }
            );
        }
    },
    GroupMembersTable: {
        userEmailFormatter: function (value, row) {
            if (value == $('#GroupOwnerEmail').val()) {
                return value + ' (Group Owner)';
            } else {
                return value;
            }

        },
        operationsFormatter: function (value, row, index) {
            if (row.email == $('#GroupOwnerEmail').val()) {
                return '';
            } else {
                return [
                    '<a class="remove btn btn-default btn-sm" href="javascript:void(0)" title="Remove">',
                    'Remove <i class="glyphicon glyphicon-remove"></i>',
                    '</a>'
                ].join('');
            }

        },
        operationEvents: {
            'click .remove': function (e, value, row, index) {
                $('#deleteGroupMemberModal').data('id', row.id).modal('show');
            }
        },
        onRemoveGroupMemberConfirm: function (e) {
            e.preventDefault();
            apis.groups.deleteMember($('#GroupID').val(), $('#deleteGroupMemberModal').data('id'),
                successCallback = function (response) {
                    // This method is called when group_to_user relationship is successfully deleted.
                    // The entry from the table is deleted.
                    $('#GroupMembersTable').bootstrapTable('remove', {
                        field: 'id',
                        values: [$('#deleteGroupMemberModal').data('id')]
                    });
                    $('#deleteGroupMemberModal').modal('hide');
                },
                errorCallback = function (xhr, status, errorThrown) {
                    // This method is called when  error occurs while deleting group_to_user relationship.
                    alert(xhr.responseText);
                });
        },
        getGroupMembers: function (params) {
            /**
             * This is the custom ajax request used to load group members in GroupMembersTable.
             *
             * params - query parameters for the ajax request.
             *          It contains parameters like limit, offset, search, sort, order.
             */

            apis.groups.getMembers($('#GroupID').val(), params.data,
                successCallback = function (response) {
                    // This method is called when members are successfully fetched.
                    params.success(response.members);
                },
                errorCallback = function () {
                    // This method is called when  error occurs while fetching members.
                    params.error('Error');
                }
            );
        }
    }
};

var joinGroupPage = {
    init: function () {
        /**
         * This function is called to setup the join group page.
         * It will initialize all the event listeners.
         */
        console.log('Loading Join Group Page....');

        $("#joinGraphSpaceBtn").click(function (e) {
            joinGroupPage.onJoinGraphSpace(e);
        });
    },
    onJoinGraphSpace: function (e) {
        e.preventDefault();
        e.preventDefault();
        var user_id = $("#joinGroupUserEmailInput").val();
        var password = $("#joinGroupUserPasswordInput").val();
        var verify_password = $("#joinGroupUserVerifyPasswordInput").val();

        if (!user_id || user_id.length == 0) {
            $.notify({
                message: 'Please enter your email!'
            }, {
                type: 'warning'
            });
            return;
        }

        if (!password || password.length == 0) {
            $.notify({
                message: 'Please enter a password for the account!'
            }, {
                type: 'warning'
            });
            return;
        }

        if (!verify_password || verify_password.length == 0) {
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
        $('#joinGraphSpaceForm').submit();
    }
};

var discussionPage = {

  presentComments: null,
  
  init: function () {
    reactions_code = [128077, 128078, 128516, 128543, 127881, 128640, 128147, 128064];
    $('#CreateCommentBtn').click(function () {
        discussionPage.createComment($('#CommentText').val());
    });

    discussionPage.getComments();

    $('.btn-default').click(function(){
        parent.history.back();
        return false;
    });
  },

    createComment: function(text) {
      console.log('creating comment');
      var owner_email = ($('#UserEmail').val() && $('#UserEmail').val() != "None")? $('#UserEmail').val() : null;
      var group_id = ($('#GroupID').val())? $('#GroupID').val() : null;
      var discussion_id = ($('#DiscussionID').val())? $('#DiscussionID').val() : null;
      if(text == "") {
          $.notify({
              message: 'Please enter a valid message'
          }, {
              type: 'danger'
          });
          return;
      }
      apis.discussion.addComment(group_id, discussion_id, {
                  "owner_email": owner_email,
                  "text": text
              },
              successCallback = function (response) {
                  $('#CommentText').val("");                  
              },
              errorCallback = function (response) {
                  $.notify({
                      message: response.responseJSON.error_message
                  }, {
                      type: 'danger'
                  });
              });
  },
  
    getComments: function () {
        var group_id = ($('#GroupID').val())? $('#GroupID').val() : null;
        var discussion_id = ($('#DiscussionID').val())? $('#DiscussionID').val() : null;
        apis.discussion.getComments(group_id, discussion_id,
              successCallback = function (response) {
                  discussionPage.commentsFormatter(response.total, response.comments);   
              },
              errorCallback = function (response) {
                  $.notify({
                      message: response.responseJSON.error_message
                  }, {
                      type: 'danger'
                  });
              });
  },
    deleteDiscussionComment: function (comment_id) {
            var comment = {
                "comment_id": comment_id
            };
            apis.discussion.deleteComment($('#GroupID').val(), $('#DiscussionID').val(), comment,
                successCallback = function (response) {
                },
                errorCallback = function (xhr, status, errorThrown) {
                    // This method is called when  error occurs while deleting comment.
                    alert(xhr.responseText);
                });
  },
    editDiscussionComment: function(text,comment_id){


            var comment = {
                "text": text,
                "comment_id": comment_id
            };

            if (!comment['text']) {
                $.notify({
                    message: 'Please enter in a valid comment!'
                }, {
                    type: 'warning'
                });
                return
            }

                apis.discussion.editComment($('#GroupID').val(), $('#DiscussionID').val(), comment,
                successCallback = function (response) {

                },
                errorCallback = function (xhr, status, errorThrown) {
                    alert(xhr.responseText);
                });
       
    },
    addCommentReaction: function (comment_id, owner_email, reaction_content) {
            var reaction = {
                "content": reaction_content,
                "owner_email": owner_email
            };
            apis.discussion.addCommentReaction($('#GroupID').val(), $('#DiscussionID').val(), comment_id, reaction, 
                successCallback = function (response) {
                },
                errorCallback = function (xhr, status, errorThrown) {
                    alert(xhr.responseText);
                });
    },
    deleteCommentReaction: function (comment_id, owner_email, reaction_content) {
            var reaction = {
                "content": reaction_content,
                "owner_email": owner_email
            };
            apis.discussion.deleteCommentReaction($('#GroupID').val(), $('#DiscussionID').val(), comment_id, reaction, 
                successCallback = function (response) {
                },
                errorCallback = function (xhr, status, errorThrown) {
                    // This method is called when  error occurs while deleting comment reaction.
                    alert(xhr.responseText);
                });
    },
    getCommentReaction: function (comment_id, reaction_content) {
            var reaction = {
                "content": reaction_content
            };
            apis.discussion.getCommentReaction($('#GroupID').val(), $('#DiscussionID').val(), comment_id, reaction, 
                successCallback = function (response) {
                    var response_reactions = response.reactions;
                    var str = "";
                    for(var i=0; i<response_reactions.length; i++){
                        str+= response_reactions[i].owner_email + '<br>'; 
                    }
                    $("#" + String(comment_id) + '-' + reaction_content + '-emoji').attr('data-original-title', str);
                    
                },
                errorCallback = function (xhr, status, errorThrown) {
                    alert(xhr.responseText);
                });
    },

  commentsFormatter: function (total, comments) {
      var ele = $('#CommentsList'); ele.html("");
      var comment_threads = [], comment_obj = {};
      var visited = {}, str = "";
      comments.forEach(function (comment) {
          if(comment.parent_comment_id == null) {
              if(comment_obj[comment.id] == null) {
                  comment_obj[comment.id] = [];
              }
              comment_obj[comment.id].push(comment);
          }
          else {
              if(comment_obj[comment.parent_comment_id] == null) {
                  comment_obj[comment.parent_comment_id] = [];
              }
              comment_obj[comment.parent_comment_id].push(comment);
          }
      });
      $.each(comment_obj, function( key, value ) {
          comment_threads.push(value);
      });
      comment_threads.forEach(function (comment_thread) {
          comment_thread.sort(function(a, b) {
              return new Date(a.created_at) - new Date(b.created_at);
          });
          var p_comment = comment_thread[0];
          str = '<div class="comment-timeline-item container-sm" id="commentContainer' + p_comment.id + '">';
          str += '<div class="panel panel-default">';
          str += discussionPage.generateCommentTemplate(p_comment);
          comment_thread.shift();
          if(comment_thread.length > 0) {
              for(var comment of comment_thread) {
                  str += discussionPage.generateCommentTemplate(comment);
              };
              str += '</div>';
              str += '</div>';
          }
          ele.append(str);

      });
      comments.forEach(function (comment) {
          discussionPage.addCommentHandlers(comment);
      });
          utils.readmoreFormatter(300);

  },
  generateCommentTemplate: function(comment) {
      var str = '<div class="panel-heading" id="commentBox' + comment.id + '">';
      var date = moment(comment.created_at).fromNow();
      str += '<b>' + comment.owner_email + '</b> <i> commented ' + date +'</i>';
      str += '<span style="float: right;">' + discussionPage.generateCommentOptions(comment) + '</i></span></div>';
      str += '<div class="panel-body" id="CommentText' + String(comment.id) + '"> <pre class = "comment-text show-read-more" id="TextDisplay' + String(comment.id) + '" value="' + String(comment.text) + '" ></pre></div>';
      str += '<div class="panel-body passive" id="EditCommentForm'+ String(comment.id) + '">';
      str += '<textarea class="pb-comment-textarea edit " id= "EditCommentText' + String(comment.id) + '"></textarea>';
      str += '<form class="form-inline">';
      str += '<button class="btn btn-success pull-right" id="UpdateCommentText' + String(comment.id) + '" type="button">Update</button>';
      str += '<button class="btn btn-danger" id="CancelCommentText' + String(comment.id) + '" type="button" style="float: right; margin-right: 20px;">Cancel</button>';
      str += '</form>';
      str += '</div>';
      str += discussionPage.displayCommentReactions(comment);
      return str;
  },
  generateCommentOptions: function(comment) {
      var str = "";
      str += '<span class="dropdown">';
      str += '<button type="button" class="btn comment-options" data-toggle="dropdown">';
      str += '<i class="fa fa-smile-o fa-lg" aria-hidden="true"></i>';
      str += '</button>';
      str += discussionPage.generateCommentReactions(comment);
      str += '</span>';
      str += '<span class="dropdown">';
      str += '<button type="button" class="btn comment-options" data-toggle="dropdown">';
      str += '<i class="fa fa-ellipsis-h fa-lg" aria-hidden="true"></i>';
      str += '</button>';
      if($('#UserEmail').val() === comment.owner_email) {
        str += '<div class="dropdown-menu " style = "min-width:80px; ">';
        str += '<a class="dropdown-item edit-comment" id="EditCommentBtn' + String(comment.id) + '">Edit</a><br>';
        str += '<a class="dropdown-item delete-comment" id="DeleteCommentBtn' + String(comment.id) + '">Delete</a><br>';
        str += '</div>';
      }
      str += '</span>';
      return str;
  },
  generateCommentReactions: function(comment) {
      var str = "";
      str += '<div class="dropdown-menu" style = "min-width:140px; ">';
      var user_reacted_emoji = [];
      for(var i=0; i<(comment.reaction_owner).length;i++){
        if(comment.reaction_owner[i]==$('#UserEmail').val())
            user_reacted_emoji.push(comment.reaction_content[i]);
      }
      for(var i=0; i<reactions_code.length; i++){
        if(user_reacted_emoji.includes(reactions_code[i])){
            str += '<span class="emoji-reacted" id="' + String(comment.id) + '-' + reactions_code[i] + '-unreact">&#' + reactions_code[i] + ';</span>';
            str += '<span class="emoji-unreacted passive" id="' + String(comment.id) + '-' + reactions_code[i] + '-react">&#' + reactions_code[i] + ';</span>';            
        }
        else{
            str += '<span class="emoji-reacted passive" id="' + String(comment.id) + '-' + reactions_code[i] + '-unreact">&#' + reactions_code[i] + ';</span>';
            str += '<span class="emoji-unreacted" id="' + String(comment.id) + '-' + reactions_code[i] + '-react">&#' + reactions_code[i] + ';</span>';
        }
      }
      str += '</div>';
      return str;
  },
  displayCommentReactions: function(comment) {
      var str = "";
      if((comment.reaction_content).length==0){
        str += '<div class="panel-footer passive" id="footer-' + String(comment.id) + '" style="height:40px;" >';
      }
      else{
        str += '<div class="panel-footer" id="footer-' + String(comment.id) + '" style="height:40px;" >';
      }
      var user_reacted_emoji = [];
      for(var i=0; i<(comment.reaction_content).length;i++){
        user_reacted_emoji.push(comment.reaction_content[i]);
      }
      var comment_unique_emojis = Array.from(new Set(user_reacted_emoji));
      for(var i=0; i<reactions_code.length; i++){
        if(comment_unique_emojis.includes(reactions_code[i])){
            str += '<span class="display-emoji" id="' + String(comment.id) + '-' + reactions_code[i] + '-emoji">&#' + reactions_code[i] + ';</span>';
        }
        else{
            str += '<span class="display-emoji passive" id="' + String(comment.id) + '-' + reactions_code[i] + '-emoji">&#' + reactions_code[i] + ';</span>';
        }
      }
      str += '</div>';
      return str;
  },
  expandTextarea: function (element) {
      element.keyup(function() {
          this.style.overflow = 'hidden';
          this.style.height = 0;
          this.style.height = this.scrollHeight + 'px';
      });
  },
  addCommentHandlers: function(comment) {
      var comment_box = $('#commentBox' + comment.id);


    $('#TextDisplay' + String(comment.id)).text(comment.text);

    $('#EditCommentBtn' + String(comment.id)).click(function(){
        $('#EditCommentForm' + String(comment.id)).removeClass("passive");
        $('#CommentText' + String(comment.id)).addClass("passive");
        $('#EditCommentText' + String(comment.id)).val($('#TextDisplay' + String(comment.id)).text());
    });

    $("#CancelCommentText" + String(comment.id)).click(function(){
        $("#EditCommentForm" + String(comment.id)).addClass("passive");
        $("#CommentText" + String(comment.id)).removeClass("passive");

    });

    $("#UpdateCommentText" + String(comment.id)).click(function(){
        discussionPage.editDiscussionComment($('#EditCommentText' + String(comment.id)).val(), comment.id);
        $("#EditCommentForm" + String(comment.id)).addClass("passive");
        $("#CommentText" + String(comment.id)).removeClass("passive");
    });

    $("#DeleteCommentBtn" + String(comment.id)).click(function(){
        discussionPage.deleteDiscussionComment(comment.id);

    });
    for(var i=0; i<reactions_code.length; i++){
        var content = reactions_code[i];
        $("#" + String(comment.id) + '-' + reactions_code[i] + '-emoji').tooltip({title: "", html: true, placement: "bottom"}); 

        $("#" + String(comment.id) + '-' + reactions_code[i] + '-emoji').hover(function(){
            content=(this.id).split("-");
            discussionPage.getCommentReaction(comment.id, content[1]);
        });

    }
    for(var i=0; i<reactions_code.length; i++){
        var content = reactions_code[i];
        $("#" + String(comment.id) + '-' + content + '-unreact').click(function(){
            content=(this.id).split("-");
            $("#" + this.id).addClass("passive");
            $("#" + (this.id).replace("unreact","react")).removeClass("passive");
            $("#" + (this.id).replace("unreact","emoji")).addClass("passive");
            discussionPage.deleteCommentReaction(comment.id, $('#UserEmail').val(), content[1]);
        });
        $("#" + String(comment.id) + '-' + content + '-react').click(function(){
            content=(this.id).split("-");
            $("#" + this.id).addClass("passive");
            $("#" + (this.id).replace("react","unreact")).removeClass("passive");
            $("#" + (this.id).replace("react","emoji")).removeClass("passive");
            if($("#footer-" + String(comment.id)).hasClass("passive")){
                $("#footer-" + String(comment.id)).removeClass("passive");
            }
            discussionPage.addCommentReaction(comment.id, $('#UserEmail').val(), content[1]);
        });
        
    }


  },

};