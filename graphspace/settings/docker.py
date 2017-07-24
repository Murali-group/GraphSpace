from graphspace.settings.base import *
from kafka import KafkaConsumer, KafkaProducer

# variables for setting up account through which GraphSpace emails
EMAIL_HOST = 'NONE'
EMAIL_HOST_USER = 'NONE'
EMAIL_HOST_PASSWORD = 'NONE'

# If error is thrown, display the error in the browser (ONLY FOR LOCAL
# MACHINES)
DEBUG = True
TEMPLATE_DEBUG = True

# URL through which to access graphspace
URL_PATH = "http://localhost/"

# If tracking is enabled for GraphSpace in Google Analytics
GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-00000000-0'

# Keys given by creating a requestor account on Amazon Mechanical Turk
# (https://www.mturk.com/mturk/welcome)
AWSACCESSKEYID = 'None'
SECRETKEY = 'None'

# Path to GraphSPace
PATH = "/home/melvin/Documents/GSoC/GraphSpace"

# SHOULD NEVER CHANGE THIS VALUE
SECRET_KEY = 'this-is-a-secret-key-for-local-settings-only'

# If needing to test on production mturk account (real money)
# AWS_URL = 'https://mechanicalturk.amazonaws.com'

# Sandbox (development) MTURK (fake money used)
AWS_URL = 'https://mechanicalturk.sandbox.amazonaws.com'

# To configure the application to use the Console Backend for sending e-mail. It writes e-mails to standard out instead of sending them.
# http://stackoverflow.com/questions/4642011/test-sending-email-without-email-server
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test',
        'USER': 'postgres',
        'PASSWORD': '987654321',
        'HOST': 'db',
        'PORT': '5431'
    }
}

# Kafka Configuration
KAFKA_URL = 'kafka'

KAFKA_CONSUMER_OWNER = {
    'bootstrap_servers': KAFKA_URL,
    'group_id': 'graphspace_owner'
}

KAFKA_CONSUMER_GROUP = {
    'bootstrap_servers': KAFKA_URL,
    'group_id': 'graphspace_group'
}

# Consumer for owner notification
KAFKA_CONSUMER = {
    "owner": KafkaConsumer('owner', **KAFKA_CONSUMER_OWNER),
    "group": KafkaConsumer('group', **KAFKA_CONSUMER_GROUP)
}

KAFKA_CONSUMER_POLL_TIMEOUT = 2

KAFKA_PRODUCER = KafkaProducer(bootstrap_servers=KAFKA_URL)
