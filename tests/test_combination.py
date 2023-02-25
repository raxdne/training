#
# Data Management for Physical Training
#
# Copyright (C) 2021,2022,2023 by Alexander Tenbusch
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.  

import sys

import math

import copy

import re

from statistics import mean

from datetime import timedelta, date, datetime, time

from icalendar import Calendar, Event, Alarm

from training import config as config
from training.description import Description
from training.title import Title
from training.note import Note
from training.unit import Unit
from training.pause import Pause
from training.combination import Combination

from suntime import Sun

print('Module Test: ' + __file__ + '\n')

# location Berlin/Germany
config.sun = Sun(52.5,13.5)
config.twilight = 1800

t = Combination([Unit('sr;3.5;RB;25:00'),
                 Pause('20min'),
                 Unit(';3.5;RB;25:00'),
                 Note('AAAA'),
                 Unit(';3.5;RB;25:00')])
#t.appendDescription('Running Blocks')
#t.remove(r'^R')
#print(t.getDuration())

t.setDate(datetime(2023, 1, 7).astimezone(None))
#t.setDate(date(2023,3,1))
print(t)

#t1 = t.dup()
#t1.setDate(date(2023,4,1))
#t1.setDate(datetime(2025, 1, 7, 22, 0).astimezone(None),datetime(2025, 1, 7, 8, 11).astimezone(None),datetime(2025, 1, 7, 16, 47).astimezone(None))
#t1.scale(2.0)
#print(t1)
#print(t1.toHtml())
#print(t1.toXML())

#print(t.toSVG(0,0))

d = {}
t.stat(d)
