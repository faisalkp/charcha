from .common import *

_debug = os.environ.get("DEBUG", 'False')
DEBUG = (_debug == "True" or _debug == "true")
ALLOWED_HOSTS = ['charcha.hashedin.com']
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS=3600
SECURE_HSTS_INCLUDE_SUBDOMAINS=False

# if os.environ.get(GCM_KEY, ''):
#     WEB_PUSH_NOTIFICATION = {
#         'GCM_KEY': os.environ.get(GCM_KEY)
#     }

# Configure logentries only if LOGENTRIES_KEY is defined in settings
if os.environ.get("LOGENTRIES_KEY", ''):
    LOGGING['handlers']['logentries'] = {
                'level': 'INFO',
                'token': os.environ.get("LOGENTRIES_KEY", ''),
                'class': 'logentries.LogentriesHandler',
                'formatter': 'verbose'
            }

    LOGGING['loggers']['charcha']['handlers'] = ['console', 'file', 'logentries']


