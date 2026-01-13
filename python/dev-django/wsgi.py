"""
WSGI config for dev-django sample.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import django
from django.conf import settings
from django.core.wsgi import get_wsgi_application

# Configure Django settings directly in code (same as in manage.py)
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='dev-secret-key-not-for-production',
        ALLOWED_HOSTS=['*'],
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.common.CommonMiddleware',
        ],
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        ROOT_URLCONF='urls',
    )
    django.setup()

application = get_wsgi_application()
