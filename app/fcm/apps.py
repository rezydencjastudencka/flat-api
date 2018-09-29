from django.apps import AppConfig


class FcmConfig(AppConfig):
    name = 'fcm'

    def ready(self):
        import fcm.signals