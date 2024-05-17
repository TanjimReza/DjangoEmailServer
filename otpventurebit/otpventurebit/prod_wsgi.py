# """
# WSGI config for otpventurebit project.

# It exposes the WSGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
# """

# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'otpventurebit.settings')

# application = get_wsgi_application()

"""
WSGI config for otpventurebit project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import signal
import subprocess

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'otpventurebit.settings')

# Start the background task process
background_task_process = subprocess.Popen(
    ['/www/otpventurebit/086639c46ee4161e9bd8ba91f646b158_venv/bin/python3',
        'manage.py', 'process_tasks'],
    preexec_fn=os.setsid,
)


def signal_handler(signal, frame):
    print('Stopping background task process...')
    os.killpg(os.getpgid(background_task_process.pid), signal.SIGTERM)
    print('Background task process stopped.')


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Get the WSGI application
application = get_wsgi_application()

# Start the WSGI application
try:
    application = get_wsgi_application()
except Exception:
    # Stop the background task process in case of any exceptions
    signal_handler(signal.SIGTERM, None)
    raise
