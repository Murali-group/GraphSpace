from graphspace.settings.base import *

# variables for setting up account through which GraphSpace emails
EMAIL_HOST = 'NONE'
EMAIL_HOST_USER = 'NONE'
EMAIL_HOST_PASSWORD = 'NONE'

# If error is thrown, display the error in the browser (ONLY FOR LOCAL MACHINES)
DEBUG = True
TEMPLATE_DEBUG = True
MAINTENANCE = False

# URL through which to access graphspace
URL_PATH = "http://localhost:8000/"

# If tracking is enabled for GraphSpace in Google Analytics
GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-00000000-0'

# Keys given by creating a requestor account on Amazon Mechanical Turk (https://www.mturk.com/mturk/welcome)
AWSACCESSKEYID = 'None'
SECRETKEY = 'None'

# Path to GraphSPace
PATH = "/Path_to_GraphSpace"

# SHOULD NEVER CHANGE THIS VALUE
SECRET_KEY = 'this-is-a-secret-key-for-local-settings-only'

# If needing to test on production mturk account (real money)
# AWS_URL = 'https://mechanicalturk.amazonaws.com'

# Sandbox (development) MTURK (fake money used)
AWS_URL = 'https://mechanicalturk.sandbox.amazonaws.com'

# To configure the application to use the Console Backend for sending e-mail. It writes e-mails to standard out instead of sending them.
# http://stackoverflow.com/questions/4642011/test-sending-email-without-email-server
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Added enviornment variable option to run with doccker-compose file and also with local dev setup
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME':  os.environ.get('POSTGRES_DB', 'graphspace'),
        'USER':  os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': '5432'
    }
}
