#! /usr/bin/env python
#-*- coding=utf-8 -*-

from setuptools import setup, find_packages


setup(name='kitabu',
      author=u'Adrian Duraj & Marek Brzóska',
      author_email='adrian.duraj@gmail.com, brzoskamarek@gmail.com',
      description="Django library to build reservation application",
      license='MIT',
      version='dev',
      url='https://github.com/mbad/kitabu',
      packages=find_packages(),
      install_requires=[
          'Django>=1.5',
          'South>=0.7.6',
      ],
      dependency_links=[
      ],
      )
