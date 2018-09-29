import logging


def notification_callback(notification_class):
    def callback(**kwargs):
        if not kwargs['action'] == 'post_add':
            return

        entity = kwargs['instance']
        affected_user_ids = kwargs['pk_set']

        notification = notification_class(entity, affected_user_ids)

        try:
            notification.send()
        except Exception:  # FIXME too broad exception clause
            logging.exception('FCM notification send failure')

    return callback
