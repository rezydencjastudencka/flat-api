#!/usr/bin/env bash

function create_config() {
  cat > "$SCRIPTS_ROOT_DIR/../app/flat_api_django/local.py"  <<EOF
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$RAILS_SECRET_KEY'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = $RAILS_DEBUG

ALLOWED_HOSTS = ['$RAILS_ALLOWED_HOST']

GCM_KEY = '$RAILS_GCM_KEY'


CORS_ORIGIN_ALLOW_ALL = $RAILS_CORS_ALLOW_ALL

CORS_ORIGIN_WHITELIST = (
    '$RAILS_CORS_WHITELIST'
)

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django_prometheus.db.backends.mysql',
        'NAME': '$RAILS_DB_NAME',
        'USER': '$RAILS_DB_USER',
        'PASSWORD': '$RAILS_DB_PASS',
        'HOST': '$RAILS_DB_HOST',
        'PORT': '$RAILS_DB_PORT',
    }
}

FCM_SERVER_KEY = '$FCM_SERVER_KEY'
EOF
}
