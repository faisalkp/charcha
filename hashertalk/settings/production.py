from common import *

DEBUG = False
ALLOWED_HOSTS = []
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SECURE_HSTS_SECONDS=3600
SECURE_HSTS_INCLUDE_SUBDOMAINS=False

# Configure logentries only if LOGENTRIES_KEY is defined in settings
if os.environ.get("LOGENTRIES_KEY", ''):
    LOGGING['handlers']['logentries'] = {
                'level': 'INFO',
                'token': os.environ.get("LOGENTRIES_KEY", ''),
                'class': 'logentries.LogentriesHandler',
                'formatter': 'verbose'
            }

    LOGGING['loggers']['hashertalk']['handlers'] = ['console', 'file', 'logentries']


