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

from training import config as config
from training.tcontainer import TContainer

from training.note import Note
from training.unit import Unit
from training.combination import Combination
#from training.plot import Plot
from training.phase import Phase
from training.cycle import Cycle
from training.bunch import Bunch

#
#
#

def CalendarYearPeriod(self,intYear,strArg=None):

    """ returns a plain calendar year period """

    try:
        date(intYear, 2, 29)
        self.append(Cycle(str(intYear),366))
    except ValueError:
        self.append(Cycle(str(intYear),365))

    if strArg is not None and strArg:
        self.setTitleStr(strArg)

    self.schedule(intYear,1,1)

    return self


def CalendarSeasonPeriod(self,intYear,strArg=None):

    """ returns a plain calendar year containing seasons periods """

    # begin of year
    d_0 = date(intYear,1,1)

    s = 'Winter {}'.format(intYear)
    # begin of spring
    d_1 = date(intYear,3,21)
    self.append(Period(s).append(Cycle(s, round((d_1 - d_0).total_seconds() / (24 * 60 * 60)))))

    s = 'Spring {}'.format(intYear)
    # begin of summer
    d_2 = date(intYear,6,21)
    self.append(Period(s).append(Cycle(s, round((d_2 - d_1).total_seconds() / (24 * 60 * 60)))))

    # begin of autumn
    s = 'Summer {}'.format(intYear)
    d_3 = date(intYear,9,21)
    self.append(Period(s).append(Cycle(s, round((d_3 - d_2).total_seconds() / (24 * 60 * 60)))))

    s = 'Autumn {}'.format(intYear)
    # begin of winter
    d_4 = date(intYear,12,21)
    self.append(Period(s).append(Cycle(s, round((d_4 - d_3).total_seconds() / (24 * 60 * 60)))))

    s = 'Winter ' + str(intYear+1)
    # begin of next year
    d_5 = date(intYear+1,1,1)
    self.append(Period(s).append(Cycle(s, round((d_5 - d_4).total_seconds() / (24 * 60 * 60)))))

    if strArg is not None and strArg:
        self.setTitleStr(strArg)

    self.schedule(intYear,1,1)

    return self


def CalendarWeekPeriod(self,intYear,strArg=None):

    """ fills a period calendar year containing week periods """

    for w in range(1,54):
        self.append(Cycle('CW{}/{}'.format(w, intYear), 7))

    d = date(intYear,1,1)
    if d.isoweekday() > 4:
        # skip to next monday
        d += timedelta(days=(8 - d.isoweekday()))
    else:
        # skip to previous monday
        d -= timedelta(days=(d.isoweekday() - 1))

    if strArg is not None and strArg:
        self.setTitleStr(strArg)

    self.schedule(d)

    return self


def CalendarMonthPeriod(self,intYear,strArg=None):

    """ returns a calendar year containing month periods """

    for m in range(1,13):
        if m > 11:
            d = date(intYear+1,1,1) - date(intYear,m,1)
        else:
            d = date(intYear,m+1,1) - date(intYear,m,1)

        self.append(Cycle('{}.{}'.format(intYear,m), d.days))

    if strArg is not None and strArg:
        self.setTitleStr(strArg)

    self.schedule(intYear)

    return self


def CalendarLastWeeksPeriod(self,intWeek=26,strArg=None):

    """ returns a last weeks as periods """

    dt_0 = datetime.now().date()
    dt_i = dt_0 + timedelta(days=(7 - dt_0.weekday())) - timedelta(weeks=intWeek)
    self.dateFixed = dt_i

    for m in range(0,intWeek):
        self.append(Cycle(dt_i.strftime("%Y-W%U")))
        dt_i += timedelta(weeks=1)

    if strArg is not None and strArg:
        self.setTitleStr(strArg)

    self.schedule()

    return self


def CalendarLastMonthsPeriod(self,intMonth=6,strArg=None):

    """ returns a last months (= 4 weeks) as periods """

    dt_0 = datetime.now().date()
    dt_i = dt_0 + timedelta(days=(7 - dt_0.weekday())) - timedelta(weeks = intMonth * 4)
    self.dateFixed = dt_i

    for m in range(0,intMonth):
        self.append(Cycle(dt_i.strftime("%Y-M%m"),4*7))
        dt_i += timedelta(weeks=4)

    if strArg is not None and strArg:
        self.setTitleStr(strArg)

    self.schedule()

    return self


if __name__ == '__main__':

    print('Module Test: ' + __file__ + '\n')
    
