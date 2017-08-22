
from django.conf import settings
#from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from graphspace.database import *
import graphspace.utils as utils
from applications.users import dal as users_db
from applications.notifications import dal as notifications_db


# Send email to users with toggle receive_notification_email = True
def send_notification_emails():
    sess = Database().session()
    limit = 10
    offset = 0
    from_email = "GraphSpace Notifications"

    while True:
        # Get users in a group of
        users = users_db.get_users_email_notification(
            db_session=sess, limit=limit, offset=offset)
        offset += limit
        serialized_users = [utils.serializer(x) for x in users]

        for u in serialized_users:
            owner_total, owner_notifications = notifications_db.find_owner_notifications(sess,
                                                                                         owner_email=u[
                                                                                             'email'],
                                                                                         is_read=False,
                                                                                         limit=10,
                                                                                         offset=0)

            owner_notifications = [utils.owner_notification_bulk_serializer(
                notify) for notify in owner_notifications]

            group_total, count_per_group = notifications_db.get_notification_count_per_group(sess,
                                                                                             member_email=u[
                                                                                                 'email'],
                                                                                             is_read=False)
            group_notifications = [{'group': utils.serializer(
                g[0]), 'count': int(g[1])} for g in count_per_group]

            total = group_total + owner_total

            if total > 0:
                html_content = render_to_string('email/notifications.html', {'host': settings.URL_PATH,
                                                                             'owner_notifications': owner_notifications,
                                                                             'group_notifications': group_notifications})
                # this strips the html, so people will have the text as well.
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives(
                    "You have " + str(total) + " unread notifications.", text_content, from_email, [u['email']])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

        #send_mail(mail_title, message, email_from, [password_reset_code.email], fail_silently=False)

        if len(users) < limit:
            break

    sess.commit()
