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
        add: function (id, data, successCallback, errorCallback) {
            console.log("gogo")
            apis.jsonRequest('POST', apis.groups.ENDPOINT + id + '/discussions', data, successCallback, errorCallback)
        },
        getSharedDiscussions: function (id, data, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.groups.ENDPOINT + id + '/discussions', data, successCallback, errorCallback)
        },
        getComments: function (group_id, discussion_id, successCallback, errorCallback) {
            apis.jsonRequest('GET', apis.groups.ENDPOINT + group_id + '/discussions/' + discussion_id, undefined, successCallback, errorCallback)
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
            console.log("jafdfdfdf");
            var discussion = {
                "topic": $("#DiscussionTopicInput").val() == "" ? undefined : $("#DiscussionTopicInput").val(),
                "message": $("#DiscussionMessageInput").val() == "" ? undefined : $("#DiscussionMessageInput").val(),
                "owner_email": $('#UserEmail').val(),
                "group_id": $('#GroupID').val()                
            };
            console.log($('#GroupID').val())
            if (!discussion['message']) {
                $('#CreateDiscussionBtn').attr('disabled', false);
                $.notify({
                    message: 'Please enter in a valid Comment'
                }, {
                    type: 'warning'
                });
                return;
            }

            apis.discussion.add($('#GroupID').val(), discussion,
                successCallback = function (response) {
                    // This method is called when group is successfully added.

                    window.location = location.pathname + '#discussions';
                    window.location.reload()


                },
                errorCallback = function (xhr, status, errorThrown) {
                    // This method is called when  error occurs while adding group.
                    if(xhr.responseJSON.error_message.includes('duplicate key')) {
                        $.notify({
                            message: 'Group name ' + discussion['message'] + ' already exists!'
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
    SharedDiscussionsTable: {
        visibilityFormatter: function (value, row) {
            if (row.is_resolved === 1) {
                return "<i class='fa fa-lock'></i> Closed";
            } else {
                return "<i class='fa fa-unlock'></i> Open";
            }
        },
        nameFormatter: function (value, row) {
            console.log("dvdfve")
            return $('<a>').attr('href', $('#GroupID').val() +'/discussions/' + row.id).text(row.topic)[0].outerHTML;
        },
        operationsFormatter: function (value, row, index) {
            return [
                '<a class="remove btn btn-default btn-sm" href="javascript:void(0)" title="Delete">',
                'Delete <i class="glyphicon glyphicon-remove"></i>',
                '</a>'
            ].join('');
        },
        operationEvents: {
            'click .remove': function (e, value, row, index) {
                $('#DeleteDiscussionModal').data('id', row.id).modal('show');
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
        getDiscussionsSharedToGroup: function (params) {
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

            apis.discussion.getSharedDiscussions($('#GroupID').val(), $('#GroupID').val(),
                successCallback = function (response) {
                    // This method is called when groups are successfully fetched.
                    params.success(response);
                    $('#groupDiscussionsTotal').text(response.total);
                },
                errorCallback = function () {
                    // This method is called when  error occurs while fetching groups.
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

    $('#createCommentBtn').click(function () {
        discussionPage.createComment($('#commentMessage').val());
    });

    discussionPage.getComments();
    $('.btn-back').click(function(){
        parent.history.back();
        return false;
    });
  },




    createComment: function(message) {
      console.log('creating comment');
      var owner_email = ($('#UserEmail').val() && $('#UserEmail').val() != "None")? $('#UserEmail').val() : null;
      var group_id = ($('#GroupID').val())? $('#GroupID').val() : null;
      var parent_discussion_id = ($('#DiscussionID').val())? $('#DiscussionID').val() : null;
      if(message == "") {
          $.notify({
              message: 'Please enter a valid message'
          }, {
              type: 'danger'
          });
          return;
      }
      apis.discussion.add(group_id, {
                  "owner_email": owner_email,
                  "group_id": group_id,
                  "message": message,
                  "parent_discussion_id": parent_discussion_id
              },
              successCallback = function (response) {
                  $('#commentMessage').val("");              
                  
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
        console.log("dveuvdcuwevgu")
        var group_id = ($('#GroupID').val())? $('#GroupID').val() : null;
        var discussion_id = ($('#DiscussionID').val())? $('#DiscussionID').val() : null;
        console.log(group_id);
      apis.discussion.getComments(group_id, discussion_id,
              successCallback = function (response) {
                  discussionPage.commentsFormatter(response.total, response.discussions);
                  console.log(response);
                  
              },
              errorCallback = function (response) {
                  $.notify({
                      message: response.responseJSON.error_message
                  }, {
                      type: 'danger'
                  });
              });
  },
  commentsFormatter: function (total, comments) {
      var ele = $('#commentsList'); ele.html(""); 
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
          str = '<div class="TimelineItem container-sm" id="commentContainer' + p_comment.id + '">';
          str += '<div class="panel panel-default">';
          str += discussionPage.generateCommentTemplate(p_comment);
          comment_thread.shift();
          if(comment_thread.length > 0) {
              // str += '<div class="collapse-comments">View all hidden replies</div>';
              // str += '<div class="collapse">';
              for(var comment of comment_thread) {
                  str += discussionPage.generateCommentTemplate(comment);
              };
              str += '</div>';
              str += '</div>';
          }
          // str += discussionPage.generateReplyTemplate(p_comment) + '</a></div>';
          ele.append(str);

          //Do setting is_resolved field if the comment is resolved.
          if(p_comment != null) {
              if(p_comment.is_resolved == 1) {
                  $('#commentContainer' + p_comment.id).data("is_resolved", 1);
                  $('#commentContainer' + p_comment.id).find('.reply-message').addClass('passive');
                  $('#commentContainer' + p_comment.id).find('.res-comment-desc').removeClass('passive');
              }
              else {
                  $('#commentContainer' + p_comment.id).data("is_resolved", 0);
              }
              if(p_comment.is_pinned !== undefined && p_comment.is_pinned == 1) {
                  $('#commentContainer' + p_comment.id).data("is_pinned", 1);
              }
              else {
                  $('#commentContainer' + p_comment.id).data("is_pinned", 0);
              }
          }
      });
      
  },
  generateCommentTemplate: function(comment) {
      if (comment.owner_email == null || comment.owner_email == "None") {
                  comment.owner_email = "Anonymous";
      }
      var str = '<div class="panel-heading" id="commentBox' + comment.id + '">';
      var date = comment.updated_at.split(/:|T/);
      var date = date[1] + ':' + date[2] + ' ' + date[0];
      str += '<b>' + comment.owner_email + '</b> on <i>' + date +'</i>';
      str += '<span style="float: right;">' + discussionPage.generateCommentOptions(comment) + '</i></span></div>';
      str += '<div class="panel-body discussion-message"><pre style="white-space: pre-line; display: contents;">' + comment.message +'</pre></div>';
      // str += '<div class="panel-footer" style="height: 40px" ></div>';
      return str;
  },
  generateCommentOptions: function(comment) {
      var str = "";
      str += '<div class="dropdown">';
      str += '<button type="button" class="btn comment-options" data-toggle="dropdown">';
      str += '<i class="fa comment-symbol">&#xf142;</i>';
      str += '</button><div class="dropdown-menu">';
      if($('#UserEmail').val() === comment.owner_email) {
          str += '<a class="dropdown-item edit-comment">Edit</a>';
          if(comment.parent_comment_id === null && comment.is_resolved === 0) {
              str += '<a class="dropdown-item resolve-comment">Resolve</a>';
          }
          str += '<a class="dropdown-item delete-comment">Delete</a>';
      }
      else if($('#UserEmail').val() === comment.graph_owner_email) {
          str += '<a class="dropdown-item delete-comment">Delete</a>';
      }
      if(comment.parent_comment_id === null) {
          if(comment.is_resolved === 1) {
              str += '<a class="dropdown-item reopen-comment">Re-open</a>';
          }
          if(comment.is_pinned === 0 || comment.is_pinned === undefined) {
              str += '<a class="dropdown-item pin-comment">Pin</a>';
          }
          else {
              str += '<a class="dropdown-item unpin-comment">Unpin</a>';
          }
      }
      str += '</div></div>';
      return str;
  },
  generateReplyTemplate: function(comment) {
      var str = "";
      str += '<textarea class="form-control reply-message" style="height:32px;"';
      str += '" placeholder="Reply.."></textarea><table class="passive reply-table" style="width: 100%"><tr>';
      str += '<td style="text-align: center; padding-top: 12px;"><a class="btn btn-primary create-reply-btn" href="#">Reply</a></td>';
      str += '<td style="text-align: center; padding-top: 12px;"><a class="btn btn-primary cancel-reply-btn" href="#">Cancel</a></td>';
      str += '</tr></table>';
      str += '<div class="passive res-comment-desc">Comment has been resolved</div>';
      return str;
  },


};