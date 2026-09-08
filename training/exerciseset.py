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
        super(Note, self).__init__()

        self.count = iArg
        self.setTitleStr(strArg)
        self.setDescription()
        self.img = []

        self.color = None


    def __repr__(self):

        strResult = f'{self.__class__.__name__}({self.strTitle!r})'
        if self.hasDescription():
            strResult += f'.appendDescription({self.listDescription!r})'

        return strResult


    def __len__(self):

        return len(self.day)


    def __str__(self):

        return f'{self.count} x {self.strTitle}'


    def getDuration(self, skipType=None):

        """  """
        
        return timedelta(seconds=self.count*2)


    def getImageRef(self):

        """  """
        
        strResult = ''
        
        for i in self.img:
            strResult += f'<img src="{i}"/>'
            
        return strResult


    def setImageRef(self,objArg):

        """  """
        
        if type(objArg) is list:
            for i in objArg:
                self.img.append(i)
        else:
            self.img.append(objArg)
        
        return self


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

        if self.count > 1:
            strResult = f'<div {config.getClass(__name__)}'
            if self.color is not None:
                strResult += ' style="background-color: {}"'.format(self.color)
            strResult += '>' + str(self) + '</div>'

        return strResult


    def toHtmlSheet(self,fImages=False):

        """  """

        strResult = ''

        if self.count > 0:
            strResult = f'<tr {config.getClass(__name__)}'
            if self.color is not None:
                strResult += ' style="background-color: {}"'.format(self.color)
            strResult += '><td>' + self.strTitle + '</td><td>' + str(self.count) + '</td><td>' + self.getDescriptionHTML() + '</td>'
            if fImages:
                strResult += '<td>' + self.getImageRef() + '</td>'
            strResult += '</tr>'

        return strResult


    def stat(self, skipType=None):

        """  """

        listResult = []
        
        #listResult = [[self.dt.toordinal(), self.dist, self.getDuration().total_seconds() / 60, self.type]]

        return listResult


    def scale(self,floatScale,patternType=None):

        """  """

        if floatScale > 0.01 and  abs(floatScale - 1.0) > 0.01:
            self.count = round(self.count * floatScale)

        return self
