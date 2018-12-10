#!/usr/bin/env python

from setuptools import setup

setup(name='tap-revinate',
      version='1.0.0',
      description='Singer.io tap for extracting data from the Revinate Porter API',
      author='Bytecode IO',
      url='http://www.singer.io',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_revinate'],
      install_requires=[
          'singer-python==5.2.0',
          'backoff==1.3.2',
          'requests==2.20.0',
          'python-dateutil==2.7.3',
          'pybase64==0.4.0',
          'pendulum==2.0.3'
      ],
      entry_points='''
          [console_scripts]
          tap-revinate=tap_revinate:main
      ''',
      packages=['tap_revinate']
)
