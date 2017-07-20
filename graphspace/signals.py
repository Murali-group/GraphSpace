from channels import Group

from json import dumps
import graphspace.utils as utils


def send_message(group_name, type, message):
    group_name = utils.websocket_group_name(group_name)
    print dumps({"type": type, "message": message})
    Group(group_name).send({'text': dumps({"type": type, "message": message})})


def send_owner_notification(notification):
    notification = utils.serializer(notification)
    notification["topic"] = "owner"
    send_message(group_name=notification[
                 'owner_email'], type="notification", message=notification)


def send_group_notification(notification):
    for notify in notification:
        serialized_notify = utils.serializer(notify)
        serialized_notify["topic"] = "group"
        send_message(group_name=serialized_notify[
                     'member_email'], type="notification", message=serialized_notify)
