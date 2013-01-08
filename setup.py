from setuptools import setup, find_packages
import sys, os

emailblast = __import__('emailblast')

readme_file = 'README.md'
try:
    long_description = open(readme_file).read()
except IOError, err:
    sys.stderr.write("[ERROR] Cannot find file specified as "
        "``long_description`` (%s)\n" % readme_file)
    sys.exit(1)

template_dir = "emailblast/templates/emailblast"
templates = [os.path.join(template_dir, f) for f in os.listdir(template_dir)]

setup(name='django-emailblast',
      version=emailblast.get_version(),
      description='Another newsletter solution for Django',
      long_description=long_description,
      zip_safe=False,
      author='Fei Tan',
      author_email='fei@argonemyth.com',
      url='https://github.com/argonemyth/django-emailblast',
      download_url='https://github.com/argonemyth/django-emailblast/downloads',
      packages = find_packages(exclude=['demo', 'demo.*']),
      package_data={'emailblast': templates}),
      include_package_data=True,
      install_requires = [
        'Django>=1.3.1',
        'celery>=3.0.10',
        'BeautifulSoup',
        'cssutils', 
        ### Required to build documentation
        # 'sphinx',
        # 'south',
      ],
      test_suite='tests.main',
      classifiers = ['Development Status :: 2 - Pre-Alpha',
                     'Environment :: Web Environment',
                     'Framework :: Django',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: BSD License',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Topic :: Utilities'],
      )
