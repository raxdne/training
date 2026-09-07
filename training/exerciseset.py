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

from pathlib import Path

import math

import copy

import re

from statistics import mean

from datetime import timedelta, date, datetime, time

from icalendar import Calendar, Event, Alarm

import numpy as np

from suntime import Sun

from training import config as config
from training.description import Description
from training.note import Note
from training.title import Title

#
#
#

class ExerciseSet(Title,Note):

    def __init__(self,strArg=None,iArg=1):

        """  """

        super(Title, self).__init__()
        super(Description, self).__init__()

        self.tChild = (iArg,strArg)

        self.setTitleStr(strArg)
        self.setDescription()

        self.color = None


    def __repr__(self):

        strResult = f'{self.__class__.__name__}({self.strTitle!r})'
        if self.hasDescription():
            strResult += f'.appendDescription({self.listDescription!r})'

        return strResult


    def __len__(self):

        return len(self.day)


    def __str__(self):

        return f'(ExerciseSet {self.tChild[0]} x {self.tChild[1]})'


    def getDuration(self, skipType=None):

        """  """
        
        return timedelta(seconds=self.tChild[0]*2)


    def dup(self):

        """  """

        return copy.deepcopy(self)


    def toString(self):

        """  """

        return str(self)


    def toStringShort(self):

        """  """

        return str(self) + self.getDescriptionString()


    def toHtmlTable(self):

        """  """

        strResult = ''

        if len(self.tChild) > 1:
            strResult = '<div'
            if self.color is not None:
                strResult += ' style="background-color: {}"'.format(self.color)
            strResult += '>' + str(self) + '</div>'

        return strResult


    def toHtmlSheet(self):

        """  """

        strResult = ''

        if len(self.tChild) > 1:
            strResult = '<tr'
            if self.color is not None:
                strResult += ' style="background-color: {}"'.format(self.color)
            strResult += '><td>' + str(self.tChild[0]) + '</td><td>' + self.tChild[1] + '</td><td>' + self.tChild[1] + '</td><td>' + self.tChild[1] + '</td></tr>'

        return strResult


    def stat(self, skipType=None):

        """  """

        listResult = []
        
        #listResult = [[self.dt.toordinal(), self.dist, self.getDuration().total_seconds() / 60, self.type]]

        return listResult


    def scale(self,floatScale,patternType=None):

        """  """

        if floatScale > 0.01 and  abs(floatScale - 1.0) > 0.01:

            n, s = self.tChild
            self.tChild = (round(n * floatScale), s)

        return self
