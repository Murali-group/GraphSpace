    //socket for comments
    var userSocket = {
        init: function() {
            var socket = new WebSocket('ws://' + window.location.host);

            socket.onopen = userSocket.onopen;

            socket.onmessage = userSocket.onmessage;

            if (socket.readyState == WebSocket.OPEN) {
                socket.onopen();
            }
        },
        onopen: function() {
            console.log('Websockets connected');
        },
        onmessage: function(message) {
            data = JSON.parse(message.data);
            // Different types of communication over sockets
            switch (data.type) {
                case "comment":
                    userSocket.getCommentToGraph(data);
                    break;
                case "discussion":
                    userSocket.discussionComments(data);
                    break;
            }
        },
        getCommentToGraph: function(data) {
            var graph_id = ($('#GraphID').val())? $('#GraphID').val() : null;
            apis.comments.getCommentToGraph(graph_id, {
                  'id': data.message.id,
              },
              successCallback = function (response) {
                  if(data.event === "insert"){
                    if(String(response.graph_id)==graph_id){
                    userSocket.comments(data);
                    }
                  }
                  else if(data.event === "delete" || data.event === "update"){
                    userSocket.comments(data);
                  }
                  
              },
              errorCallback = function (response) {
              });
        },
        // Socket communication for comments
        comments: function(data) {
            var graph_id = ($('#GraphID').val())? parseInt($('#GraphID').val()) : null;
            if(data.event === "insert") {
                userSocket.addcomment(data.message);
            }
            else if(data.event === "update") {
                userSocket.updatecomment(data.message);
            }
            else if(data.event === "delete") {
                userSocket.deletecomment(data.message);
            }
        },
        addcomment: function(comment) {
            var str = "";
            if(comment.parent_comment_id != null) {
                str += graphPage.generateCommentTemplate(comment);
                $(str).insertBefore($("#commentContainer" + comment.parent_comment_id).find('.reply-message'));
                $('#commentContainer' + comment.parent_comment_id).find('.reply-table').addClass('passive');
            }
            if(comment.parent_comment_id == null) {
                var ele = $('#CommentsList');
                var str = "";
                str += '<div class="list-group comment-box" id="commentContainer' + comment.id + '">';
                str += '<a class="list-group-item comment-highlight">';
                str += graphPage.generateCommentTemplate(comment);
                str += graphPage.generateReplyTemplate(comment) + '</a></div>';
                ele.append(str);
            }
            graphPage.addCommentHandlers(comment);
        },
        updatecomment: function(comment) {
            ele  = $('#commentBox' + comment.id);
            ele.find('.comment-text').text(comment.text);
            ele.find('.cancel-edit-btn').click();
            if(comment.parent_comment_id == null && comment.is_closed == 1) {
                $('#commentContainer' + comment.id).data("is_closed", 1);
                //styling for resolved comments
                $('#commentContainer' + comment.id).find('.reply-message').addClass('passive');
                $('#commentContainer' + comment.id).find('.res-comment-desc').removeClass('passive');
                //ended styling
                var box = $('#commentBox' + comment.id).find('.resolve-comment');
                box.removeClass('resolve-comment').addClass('reopen-comment'); box.html("Re-open");
                box.unbind('click').click(function (e) {
                    e.preventDefault();
                    var ele = $('#commentBox' + comment.id);
                    var comment_id = parseInt(ele.attr('id').split("commentBox")[1]);
                    graphPage.editComment(comment_id, undefined, 0);
                });
            }
            if(comment.parent_comment_id == null && comment.is_closed == 0) {
                $('#commentContainer' + comment.id).data("is_closed", 0);
                //styling for reopened comments
                $('#commentContainer' + comment.id).find('.reply-message').removeClass('passive');
                $('#commentContainer' + comment.id).find('.res-comment-desc').addClass('passive');
                //ended styling
                var box = $('#commentBox' + comment.id).find('.reopen-comment');
                box.removeClass('reopen-comment').addClass('resolve-comment'); box.html("Resolve");
                box.unbind('click').click(function (e) {
                    e.preventDefault();
                    var ele = $('#commentBox' + comment.id);
                    var comment_id = parseInt(ele.attr('id').split("commentBox")[1]);
                    graphPage.editComment(comment_id, undefined, 1);
                });
            }
        },
        deletecomment: function(comment) {
            if(comment.parent_comment_id == null) {
                $('#commentContainer' + comment.id).remove();
            }
            if(comment.parent_comment_id != null) {
                if($('#commentContainer' + comment.parent_comment_id).find('.collapse').children().length == 1) {
                    $('#commentContainer' + comment.parent_comment_id).find('.collapse').remove();
                    $('#commentContainer' + comment.parent_comment_id).find('.collapse-comments').remove();
                }
                else {
                    ($('#commentBox' + comment.id))? $('#commentBox' + comment.id).remove() : null;
                }
            }
        },
        discussionComments: function(data){
            if(data.event === "insert_comment") {
                userSocket.addDiscussionComment(data.message);
                is_event = true;
            }
            else if(data.event === "update_comment") {
                userSocket.editDiscussionComment(data.message);
                is_event = true;
            }
            else if(data.event === "delete_comment") {
                userSocket.deleteDiscussioncomment(data.message);
                is_event = true;
            }
            else if(data.event === "close") {
                userSocket.resolveDiscussion(data.message);
                is_event = true;
            }
            else if(data.event === "reopen") {
                userSocket.reopenDiscussion(data.message);
                is_event = true;
            }
            else if(data.event === "delete_discussion") {
                userSocket.deleteDiscussion(data.message);
                is_event = true;
            }
        },
        addDiscussionComment: function(comment) {
            if(location.pathname==('/groups/'+ comment.group_id[0] +'/discussions/' + comment.discussion_id[0])){
            var str = "";
                var ele = $('#CommentsList');
                str = '<div class="comment-timeline-item container-sm" id="commentContainer' + comment.id + '">';
                str += '<div class="panel panel-default">';
                str += discussionPage.generateCommentTemplate(comment);
                str += '</div>';
                str += '</div>';
                ele.append(str);
            discussionPage.addCommentHandlers(comment);
        }
        },
        
        deleteDiscussioncomment: function(comment) {
                $('#commentContainer' + comment.id).remove();            
        },
        deleteDiscussion: function(discussion) {
                $('#DiscussionRow' + discussion.id).remove();
                if(location.pathname==('/groups/'+ discussion.group_id +'/discussions/' + discussion.id)){
                    var str ='/groups/'+ discussion.group_id + '#discussions';
                    window.location = str;
                }
            
        },
        editDiscussionComment: function(comment) {
                $('#TextDisplay' + String(comment.id)).text(comment.text);
        },

        resolveDiscussion: function(discussion) {
            if(location.pathname==('/groups/' + discussion.group_id)){
                $('.discussion-unlock' + String(discussion.id)).addClass("passive");
                $('.discussion-lock' + String(discussion.id)).removeClass("passive");
            }
            if(location.pathname==('/groups/'+ discussion.group_id +'/discussions/' + discussion.id)){
                window.location=location.pathname;
            }
        },
        reopenDiscussion: function(discussion) {
            if(location.pathname==('/groups/'+ discussion.group_id +'/discussions/' + discussion.id)){
                window.location=location.pathname;
            }
            if(location.pathname==('/groups/'+ discussion.group_id)){
                $('.discussion-lock' + String(discussion.id)).addClass("passive");
                $('.discussion-unlock' + String(discussion.id)).removeClass("passive");
            }
        },
    }