#
# Data Management for Physical Training
#
# Copyright (C) 2021,2022,2023,2026 by Alexander Tenbusch
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

import io

import os

from pathlib import Path

import sys

import math

import copy

import re

from statistics import mean

from datetime import timedelta, date, datetime, time, timezone

from suntime import Sun

from icalendar import Calendar, Event, Alarm

import numpy as np

from training.note import Note
from training.pause import Pause
from training.unit import Unit
from training.exerciseset import ExerciseSet
from training.combination import Combination
from training.cycle import Cycle
from training.period import Period
from training.phase import Phase
from training.bunch import Bunch

from training import config as config

def parseFile(objContainer, listFilename, fUpdater=None):

    """  """

    if type(listFilename) is str:
        listFilename = [listFilename]

    a = []
    d0 = None
    d1 = None
    t = Unit()
    n = Note()

    for filename in listFilename:
        print("* ", filename, file=sys.stderr)
        with open(filename) as f:
            content = f.read().splitlines()
        f.close()

        d_i = None
        for l in content:
            if l is None or l == '' or re.match(r"^sep", l) or re.match(r"^\*", l):
                pass
            elif (fUpdater is not None and t.parse(fUpdater(l))) or t.parse(l):
                if t.dt is not None:
                    d_i = t.dt
                    if d0 is None or t.dt < d0:
                        d0 = t.dt
                    if d1 is None or t.dt > d1:
                        d1 = t.dt
                else:
                    t.dt = d_i

                a.append(t)
                t = Unit()
            elif (fUpdater is not None and n.parse(fUpdater(l))) or n.parse(l):
                if n.dt is not None:
                    d_i = n.dt
                    if d0 is None or n.dt < d0:
                        d0 = n.dt
                    if d1 is None or n.dt > d1:
                        d1 = n.dt
                else:
                    n.dt = d_i

                a.append(n)
                n = Note()
            else:
                print('error: ' + l, file=sys.stderr)

            if d1 is None and d0 is not None:
                d1 = d0

    if d0 is None:
        print('error: No start date found', file=sys.stderr)
    elif d1 is None:
        print('error: No end date found', file=sys.stderr)
    else:
        delta = d1 - d0

        if objContainer is None:
            objContainer = Period('')
        elif len(objContainer.child) > 0:
            # there is a child list already
            pass
        elif delta.days < 365:
            for y in range(d0.year, d1.year+1):
                objContainer.append(CalendarWeekPeriod(y))
        elif delta.days < 3 * 365:
            for y in range(d0.year, d1.year+1):
                objContainer.append(CalendarMonthPeriod(y))
        else:
            for y in range(d0.year, d1.year+1):
                objContainer.append(CalendarYearPeriod(y))

        for t in a:
            c = objContainer.getContainerByDate(t.dt)
            if c is None:
                print('error: out of date range ' + str(t), file=sys.stderr)
            else:
                c.insertByDate(t)

    objContainer.setPlan(False)
    
    return objContainer


if __name__ == '__main__':

    print('Module Test: ' + __file__ + '\n')
    
