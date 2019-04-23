DEBUG = True
ROOT_URLCONF = 'urls'
SECRET_KEY = 'ooo'
ALLOWED_HOSTS = ['*']

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': ['templates'],
}]
