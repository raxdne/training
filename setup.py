#
# Copyright (C) 2021 by Alexander Tenbusch
#

from distutils.core import setup

setup(name='training',
      version='1.16',
      description='simple Data Management for Physical Training',
      author='Alexander Tenbusch',
      author_email='raxdne@web.de',
      url='https://github.com/raxdne/training',
      packages=['training'],
      scripts=['report.py'],
      install_requires=['suntime','icalendar'],
     )
