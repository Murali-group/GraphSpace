from channels import Group

from json import dumps
import graphspace.utils as utils


def send_message(group_name, type, message):
    group_name = utils.websocket_group_name(group_name)
    print dumps({"type": type, "message": message})
    Group(group_name).send({'text': dumps({"type": type, "message": message})})


def send_notification(notification, topic):
    notification = utils.serializer(notification)
    group_name_attr = {
        "owner": "owner_email",
        "group": "member_email"
    }
    notification["topic"] = topic
    send_message(group_name=notification[group_name_attr[
                 topic]], type="notification", message=notification)
