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

from abc import ABC, abstractmethod
from typing import final
from statistics import mean

from datetime import timedelta, date, datetime, time, timezone

from suntime import Sun

from icalendar import Calendar, Event, Alarm

from training import config as config
from training.ttitle import TTitle
from training.tdescription import TDescription

#
#
#

class TItem(TTitle,TDescription):

    def __init__(self,strArg=None):

        """  """

        super(TTitle, self).__init__()
        super(TDescription, self).__init__()
        #super(Plot, self).__init__()

        self.setTitleStr(strArg)
        self.dt = None
        self.tPlan = None
        self.marker = False
        self.color = None


    @abstractmethod
    def __str__(self):

        """  """
        
        pass


    def __enter__(self):

        """  """

        return self


    def __exit__(self, exc_type, exc_value, exc_tb):    

        """  """

        pass        


    @abstractmethod
    def stat(self, skipType=None):

        """  """

        pass


    def getColor(self):

        """  """
        
        strResult = ''
        
        if self.color is not None:
            strResult = self.color

        return strResult


    def mark(self):

        """  """

        self.marker = True

        return self


    def isMarked(self):

        """  """

        return hasattr(self,'marker') and self.marker == True


    def setClock(self,timeArg=None):

        """  """

        self.tPlan = timeArg

        return True


    def setDate(self,dtArg=None,dt_0=None,dt_1=None):

        """  """

        if dtArg is None:
            self.dt = None
        elif type(dtArg) is date:
            if self.tPlan is None:
                return self.setDate(datetime.combine(dtArg,time(0)).astimezone(None),dt_0,dt_1)
            else:
                return self.setDate(datetime.combine(dtArg,self.tPlan).astimezone(None),dt_0,dt_1)
        elif type(dtArg) is datetime:
            if self.tPlan is not None and dtArg.time() == time(0):
                return self.setDate(datetime.combine(dtArg.date(),self.tPlan).astimezone(None),dt_0,dt_1)
            else:
                self.dt = dtArg
                return self.dt
        else:
            print('error: date ' + str(dtArg), file=sys.stderr)

        return None


    def setDateStr(self,strArg):

        """  """

        if strArg is None or strArg == '':
            pass
        elif strArg == '+':
            # it's a combined unit (starts after its predecessor unit, same date)
            pass
        elif strArg == 'sr':
            self.tPlan = 'sunrise'
        elif strArg == 'ss':
            self.tPlan = 'sunset'
        else:
            # canonical ISO Date+Time
            m = re.match(r'\s*([0-9]{4}-*[0-9]{2}-*[0-9]{2})[\sT]+([0-2][0-9]:*[0-5][0-9]:*[0-5][0-9])(\+[0-1]*[0-9])*\s*',strArg)
            if m is not None:
                try:
                    self.dt = datetime.fromisoformat(m.group(1) + 'T' + m.group(2)).astimezone(None)
                except ValueError as e:
                    print('error: ' + str(e), file=sys.stderr)
                    return False
            else:
                # german Date
                m = re.match(r'\b([0-9]{2})\.([0-9]{2})\.([0-9]{4})\b',strArg)
                if m is not None:
                    try:
                        self.dt = datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)),0,0,0).astimezone(None)
                    except ValueError as e:
                        print('error: ' + str(e), file=sys.stderr)
                        return False
                else:
                    # canonical ISO Date
                    m = re.match(r'\b([0-9]{4})-*([0-9]{2})-*([0-9]{2})\b',strArg)
                    if m is not None:
                        try:
                            self.dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),0,0,0).astimezone(None)
                        except ValueError as e:
                            print('error: ' + str(e), file=sys.stderr)
                            return False
                    else:
                        # plan time only
                        m = re.match(r'\b([0-2][0-9]:[0-5][0-9])\b',strArg)
                        if m is not None:
                            #print("time: ",m.group(1), file=sys.stderr)
                            self.tPlan = time.fromisoformat(m.group(1) + ':00')
                        else:
                            print('ignoring: ',strArg, file=sys.stderr)

        return True


    @final
    def dup(self):

        """  """

        return copy.deepcopy(self)


    def toString(self):

        """  """

        return str(self)



