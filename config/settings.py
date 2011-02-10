# Django settings for majenta project.
import imp
import sys
from os import path
import os

# Path to the django project (mainsite)
PROJECT_DIR = path.abspath(path.dirname(__file__).decode('utf-8'))
# Path to the whole project (one level up from mainsite)
TOP_DIR = path.abspath(path.dirname(PROJECT_DIR).decode('utf-8'))
# Required python libraries should go in this directory 
LIB_DIR = path.join(TOP_DIR,"lib")
# Apps written for the project go in this directory
APP_DIR = path.join(TOP_DIR,"apps")
# Prepend LIB_DIR, PROJECT_DIR, and APP_DIR to the PYTHONPATH
for p in (PROJECT_DIR, LIB_DIR, APP_DIR, TOP_DIR):
    if p not in sys.path:
        sys.path.insert(0,p)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATE_FORMAT='d M Y'

ADMINS = (
     ('BizNet Team', 'admin@bluerain.in'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'biznet',                      # Or path to database file if using sqlite3.
        'USER': 'biznet',                      # Not used with sqlite3.
        'PASSWORD': 'biznet',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path.join(TOP_DIR,"public")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/public/'
ADMIN_MEDIA_PREFIX = '/media/'
USER_FILES_LOCATION = os.path.join(os.path.dirname(__file__), 'userfiles').replace('\\','/')
UPLOAD_DIR='files'


# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '9o#!d*1i=q7_!@wc!!xltz*#v9li&=^=^i)5lb7e$^k+%0+(z1'

# List of callables that know how to import templates from various sources.
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    'djangoflash.context_processors.flash',
    'util.context_processors.media_url',
    'util.context_processors.date_format',
    'util.context_processors.today',
    'util.context_processors.template',
    'util.context_processors.app_details',
    'util.context_processors.theme',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'djangoflash.middleware.FlashMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'util.middleware.CheckUnconfirmedUserMiddleware',
    'util.middleware.SetupIEP3PMiddleware',    
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS =( 
    path.join(TOP_DIR,"templates"),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
)

THIRD_PARTY_APPS=(
  #  'south',
  #  'registration',
  #  'tagging',
  #  'tagging_autocomplete',
  #  'threadedcomments',
  #  'django_extensions',
)

APPS=(
    'util',
)
LOGIN_URL = '/'
INSTALLED_APPS=DJANGO_APPS+THIRD_PARTY_APPS+APPS


UI_DATE_FORMAT='dd/mm/yy'
APP_NAME='<APP NAME>'
APP_DESC='<Great App!>'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST=''
#EMAIL_HOST_USER=''
#EMAIL_HOST_PASSWORD=''
#AUTH_PROFILE_MODULE = ''


def load_local_settings():
    """
    Load the settings defined in the mainsite.local_settings module.

    Once all settings are loaded, call local_settings.setup with a
    dictionary of the final settings.
    """
    from config import local_settings

    def filter_settings(settings_dict):
        """
        Filters a dict by uppercase keys.  Returns a new dictionary
        which contains only the items which have uppercase keys.
        """
        return dict(
            filter(lambda (k, v): k.isupper(), settings_dict.items())
        )

    settings_dict = globals() # dict of our main settings.

    # Update main settings with the local_settings.
    settings_dict.update(
        # Filter out functions and __special__ keys.
        filter_settings(local_settings.__dict__)
    )

    # If local_settings has a 'setup' function then call it with our
    # final settings dict.
    if hasattr(local_settings, 'setup') and callable(local_settings.setup):
        local_settings.setup(settings_dict)

# Load additional settings from the mainsite.local_settings module,
# if it exists.

try:
    # Check if it exists.
    imp.find_module('local_settings', [PROJECT_DIR])
except ImportError:
    pass
else:
    load_local_settings()

