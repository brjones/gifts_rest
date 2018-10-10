import os

ENV = os.getenv('DJANGO_ENVIRONMENT', 'development')

try:
    FALLOVER = bool(int(os.getenv('FALLOVER', "0")))
except ValueError:
    FALLOVER = False

DEV_ENV  = ENV == 'development'
TEST_ENV = ENV == 'staging'
PROD_ENV = ENV == 'production'
