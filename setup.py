#
# Copyright (C) 2021,2022 by Alexander Tenbusch
#

from distutils.core import setup

setup(name='training',
      version='2.0',
      description='simple Data Management for Physical Training',
      author='Alexander Tenbusch',
      author_email='raxdne@web.de',
      url='https://github.com/raxdne/training',
      packages=['training'],
      scripts=['report.py'],
      install_requires=['suntime','icalendar'],
     )
