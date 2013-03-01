Kitabu
======

This is a Django application meant as a library to build reservations into existing (or under construction) project. 

The app delivers base classes to mix in to existing models. It delivers only one ready (non abstract) model - Validator. The Validator model is meant as base model for django multi-table inheritance for your own custom validators (examples we thought would be useful are included).


Most abstract models are ready to use, just pick classes that include functionality you are interested in and mix in as your models' base classes.

For now, most complete documentation is example project included with the distribution.

Installation
------------

1. `pip install -e git+https://github.com/mbad/kitabu.git#egg=django_kitabu-dev`
1. Add `'kitabu'` to you INSTALLED_APPS

Installation for development
----------------------------

1. Clone
1. Run `python setup.py develop`
1. Develop. You can run example project from `example_project` directory, the usual django way: `python manage.py runserver`. You probably also want to install requirements: `pip install -r requirements.txt` and create local database: `python manage.py syncdb --migrate`.

Heroku
------

Example project is ready to deploy on Heroku. ``requirements.txt`` and ``Procfile`` files in the main directory are all that heroku expects.

