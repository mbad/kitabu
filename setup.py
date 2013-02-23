#! /usr/bin/env python
#-*- coding=utf-8 -*-

from setuptools import setup


setup(name='kitabu',
      author=u'Adrian Duraj & Marek Brzóska',
      author_email='adrian.duraj@gmail.com, brzoskamarek@gmail.com',
      description="Django library to build reservation application",
      license='MIT',
      version='dev',
      url='https://github.com/mbad/kitabu',
      packages=['kitabu'],
      #include_package_data=True,
      install_requires=[
          'Django>=1.5c1',
          'South>=0.7.6',
      ],
      dependency_links=[
          'http://github.com/django/django/tarball/1.5c1#egg=Django-1.5c1',
      ],
      )
