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
from training.tcontainer import TContainer

from training.note import Note
from training.unit import Unit
from training.combination import Combination
from training.exerciseset import ExerciseSet
#from training.plot import Plot
from training.phase import Phase
from training.cycle import Cycle
from training.bunch import Bunch


from suntime import Sun

print('Module Test: ' + __file__ + '\n')

t = Bunch('TEST',3*7).schedule(2023,12,8)

t.append((12,Unit(';30;BB;01:10:00')))
t.append((7,Unit(';10;BR;01:00:00')))
t.appendDescription('Running Blocks')
t.scale(1.25)
    
print(t)
