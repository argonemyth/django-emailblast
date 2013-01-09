Django EmailBlast
=================

EmailBlast is a Django application that sends HTMLs or text newsletters. At the moment, there is no front-end interface like the subscription forms, you will have to do everything in the admin.


Features
========

* Subscribers can be a User or someone with a name or email.
* Can send HTML emails, although you will need to code the email template.
* You can resume the sending if something wen wrong. 


Requirements
============

* Django>=1.3.1
* celery>=3.0.10 
* BeautifulSoup
* cssutils

Usage
=====

Installation
------------

Since the app relies on Django celery to send emails, we will also cover how to setup the celery.

1. Install the app:

```
$ pip install git+https://github.com/argonemyth/django-emailblast.git
```

2. Add 'djcelery' and 'emailblast' to `INSTALLED_APPS` in settings.py:

```python
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    ...
    'djcelery',
    'mailblast',
    ) 
```

3. Add necessery configurations for celery:

```python
# Django Celery
import djcelery
djcelery.setup_loader()

# Celery Broker settings.
BROKER_URL = 'amqp://guest:guest@localhost:5672/'

# List of modules to import when celery starts.
CELERY_IMPORTS = ("emailblast.tasks", )
```

4. Syncdb

If you have south installed:

    $ python manage.py migrate emailblast

if not, just syncdb:

    $ python manage.py syncdb 

