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
from training.exerciseset import ExerciseSet
from training.combination import Combination

from suntime import Sun

print('Module Test: ' + __file__ + '\n')

# location Berlin/Germany
config.sun = Sun(52.5,13.5)
config.twilight = 1800

def Liegestütz(n=1):

    return ExerciseSet('Liegestütz',n).appendDescription('flach')

c = Combination([Liegestütz(12),ExerciseSet('E1',24),Pause('10min','Halt'),ExerciseSet('E2',24),ExerciseSet('E3',24)]).setTitleStr('My Circle')

t = Combination([Unit('08:11:00;3.5;RB;25:00'),
                 Pause('20min'),
                 Unit(';3.5;RB aa;20:30'),
                 Note('AAAA'),
                 Unit(';3.5;RB;25:00'),
                 Pause('10min','Halt'),
                 c])

s = Combination([c,c.scale(1.333),c])
t = Combination([s,s.scale(1.333),s])
#t = Combination()
#t.append(c)
#t.append(c.scale(2.0))
#t.append(c)

#t.setDate(datetime(2025, 1, 7, 8, 11).astimezone(None))
#t.setDate(date(2023,3,1))
print(t)
print(t.toStringShort())
#print(t.toFreemindNode())
print(t.toHtmlTable())

t = Combination([Combination([Unit('sr;3.5;AB;25:00'), Pause('20min'), Unit(';3.5;BB;25:00')]),
                 Unit(';3.5;RB;25:00')],
                 False)

#t.appendDescription('Running Blocks')
#t.setTitleStr('My Combination')
#t.remove(r'^R')
#print(t.getDuration())
#print(t.getRepresentativeAlternative())

#t.setDate(datetime(2023, 1, 9).astimezone(None))
t.setDate(date(2023,3,1))
#t.mark()
#t.scale(0.009)
#print(t.isMarked())
print(t)
print(t.stat())
#print(t.toStringShort())
#print(t.toFreemindNode())
#print(t.toHtmlTable())
#print(t.stat())

f = open('plan.html', 'w')
f.write(t.toHtmlFile(True))
f.close()

#t1 = t.dup()
#t1.setDate(date(2023,4,1))
#t1.setDate(datetime(2025, 1, 7, 22, 0).astimezone(None),datetime(2025, 1, 7, 8, 11).astimezone(None),datetime(2025, 1, 7, 16, 47).astimezone(None))
#t1.scale(2.0)
#print(t1)
#print(t1.toHtml())
#print(t1.toXML())

#print(t.toSVG(0,0))

cal = Calendar()
#cal.add('prodid', '-//{title}//  //'.format(title=self.getTitleString()))
cal.add('version', '2.0')
t.to_ical(cal)

f = open('plan.ics', 'wb')
f.write(cal.to_ical())
f.close()

