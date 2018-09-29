import logging


def discard_creator(creator_id, affected_user_ids):
    recipient_ids = set(affected_user_ids)
    recipient_ids.discard(creator_id)
    return recipient_ids


def build_notification(notification_class, entity, affected_user_ids):
    recipient_ids = discard_creator(entity.from_user_id, affected_user_ids)
    return notification_class(entity, recipient_ids)


def notification_callback(notification_class):
    def callback(**kwargs):
        if not kwargs['action'] == 'post_add':
            return

        entity = kwargs['instance']
        affected_user_ids = kwargs['pk_set']

        notification = build_notification(notification_class, entity, affected_user_ids)

        try:
            notification.send()
        except Exception:  # FIXME too broad exception clause
            logging.exception('FCM notification send failure')

    return callback
