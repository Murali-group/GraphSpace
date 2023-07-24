from graphspace.settings.base import *

# variables for setting up account through which GraphSpace emails
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# If error is thrown, display the error in the browser (ONLY FOR LOCAL MACHINES)
DEBUG = os.environ.get('DEBUG')
TEMPLATE_DEBUG = os.environ.get('TEMPLATE_DEBUG')
MAINTENANCE = os.environ.get('MAINTENANCE')

# URL through which to access graphspace
URL_PATH = os.environ.get('URL_PATH')

# If tracking is enabled for GraphSpace in Google Analytics
GOOGLE_ANALYTICS_PROPERTY_ID = os.environ.get('GOOGLE_ANALYTICS_PROPERTY_ID')

# Keys given by creating a requestor account on Amazon Mechanical Turk (https://www.mturk.com/mturk/welcome)
AWSACCESSKEYID = os.environ.get('AWSACCESSKEYID')
SECRETKEY = os.environ.get('SECRETKEYOST')

# Path to GraphSPace
PATH = os.environ.get('PATH', '/path_to_graphspace')

# SHOULD NEVER CHANGE THIS VALUE
SECRET_KEY = os.environ.get('SECRET_KEY')

# If needing to test on production mturk account (real money)
# AWS_URL = 'https://mechanicalturk.amazonaws.com'

# Sandbox (development) MTURK (fake money used)
AWS_URL = os.environ.get('AWS_URL')

# To configure the application to use the Console Backend for sending e-mail. It writes e-mails to standard out instead of sending them.
# http://stackoverflow.com/questions/4642011/test-sending-email-without-email-server
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME':  os.environ.get('POSTGRES_DB'),
        'USER':  os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': os.environ.get('POSTGRES_PORT')
    }
}
