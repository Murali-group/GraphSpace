from channels import Group

from json import dumps
import re
import graphspace.utils as utils

def send_message(group_name, type, message, event):
    group_name = utils.websocket_group_name(group_name)
    Group(group_name).send({'text': dumps({"type": type, "message": message, "event": event})})


def send_comment(comment, type, users=None, event=None):
    comment = utils.serializer(comment)
    if type == 'private':
    	email_list = []
        if users:
            for user in users:
                user = utils.serializer(user)
                email_list.append(user['email'])
            email_list.append(comment['owner_email'])
            email_list = list(set(email_list))
        for email in email_list:
            send_message(group_name=email, type="comment", message=comment, event=event)
    elif type == 'public':
        send_message(group_name='anonymous@anonymous.com', type="comment", message=comment, event=event)

def send_discussion(discussion, type, users=None, event=None):
    discussion = utils.serializer(discussion)
    if type == 'private':
    	email_list = []
        if users:
            for user in users:
                user = utils.serializer(user)
                email_list.append(user['email'])
            email_list = list(set(email_list))
        for email in email_list:
            send_message(group_name=email, type="comment", message=discussion, event=event)