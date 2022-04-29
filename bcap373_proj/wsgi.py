"""
WSGI config for bcap373_proj project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import logging

from dj_static import Cling

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bcap373_proj.settings')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)-8s %(message)s",
)

application = get_wsgi_application()
