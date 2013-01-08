Django EmailBlast
=================

EmailBlast is a Django application that sends HTMLs or text newsletters.

Requirements
============

* Django>=1.3.1
* celery>=3.0.10 
* BeautifulSoup
* cssutils

Celery Setup
============

To test the app locally after installing & setup django celery:

$ python manage.py celery worker --loglevel=info
