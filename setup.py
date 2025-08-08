#!/usr/bin/env python

from setuptools import setup

setup(name='tap-revinate',
      version='1.0.1',
      description='Singer.io tap for extracting data from the Revinate Porter API',
      author='Bytecode IO',
      url='http://www.singer.io',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_revinate'],
      install_requires=[
          'singer-python==5.13.2',
          'backoff==1.10.0',
          'requests==2.32.4',
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
