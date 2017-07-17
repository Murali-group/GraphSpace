from channels import Group

from json import dumps
import graphspace.utils as utils


def send_notification(group_name, notification):
    group_name = utils.websocket_group_name(group_name)
    Group(group_name).send({'text': dumps(notification)})


def send_owner_notification(notification):
    notification = utils.serializer(notification)
    notification["topic"] = "owner"
    send_notification(group_name=notification[
                      'owner_email'], notification=notification)


def send_group_notification(notification):
    for notify in notification:
        serialized_notify = utils.serializer(notify)
        serialized_notify["topic"] = "group"
        send_notification(group_name=serialized_notify[
                          'member_email'], notification=serialized_notify)
