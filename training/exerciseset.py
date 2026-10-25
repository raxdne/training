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
from training.titem import TItem

#
#
#

class ExerciseSet(TItem):

    def __init__(self,strArg=None,iArg=1):

        """  """

        super().__init__(strArg)

        self.repetitions = iArg
        self.img = []
        self.setDescription()
        self.setShortNote()


    def __repr__(self):

        strResult = f'{self.__class__.__name__}({self.strTitle!r})'
        if self.hasDescription():
            strResult += f'.appendDescription({self.listDescription!r})'

        return strResult


    def __len__(self):

        return len(self.child)


    def __str__(self):

        return f'{self.repetitions} x {self.strTitle} {self.strNote}'


    def getRepetitions(self):

        """  """
        
        return self.repetitions


    def getDuration(self, skipType=None):

        """  """
        
        return timedelta(seconds=self.repetitions * 3)


    def getImageRef(self):

        """  """
        
        strResult = ''
        
        for i in self.img:
            strResult += f'<img src="{i}"/>'
            
        return strResult


    def setImageRef(self,o):

        """  """
        
        if type(o) is list:
            for i in o:
                self.img.append(i)
        else:
            self.img.append(o)
        
        return self


    def getShortNote(self):

        """  """
        
        return self.strNote


    def setShortNote(self,strArg=''):

        """  """
        
        self.strNote = strArg
                
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

        if self.repetitions > 1:
            strResult = f'<div {config.getClass(__name__)}'
            if self.color is not None:
                strResult += f' style="background-color: {self.color}"'
            strResult += '>' + str(self) + '</div>'

        return strResult


    def toHtmlSheet(self,fImages=True,fDescription=True):

        """  """

        strResult = ''

        if self.repetitions > 0:
            #strResult = f'<tr {config.getClass(__name__)}'
            #if self.color is not None:
            #    strResult += f' style="background-color: {self.color}"'
            #strResult += '>'
            #strResult += '<td>' + str(self.getDuration()) + '</td>'
            strResult += '<td>' + self.strTitle + ' ' + self.strNote + '</td><td>' + str(self.repetitions) + '</td>'
            if fDescription:
                strResult += '<td>' + self.getDescriptionHTML() + '</td>'
            if fImages:
                strResult += '<td>' + self.getImageRef() + '</td>'
            #strResult += '</tr>'

        return strResult


    def toFreemindNode(self):

        """  """

        strResult = '<node LOCALIZED_STYLE_REF="default"'
        if self.color is not None:
            strResult += f' BACKGROUND_COLOR="{self.color}"'
        strResult += ' TEXT="' + self.getTitleXML() + ' x ' + str(self.repetitions) + '"/>'

        return strResult


    def stat(self, skipType=None):

        """  """

        listResult = []
        
        #listResult = [[self.dt.toordinal(), self.dist, self.getDuration().total_seconds() / 60, self.type]]

        return listResult


    def scale(self,floatScale,patternType=None):

        """ returns a scaled copy of self """

        r = self.dup()
        if floatScale > 0.01 and  abs(floatScale - 1.0) > 0.01:
            r.repetitions = round(r.repetitions * floatScale)

        return r


if __name__ == '__main__':

    print('Module Test: ' + __file__ + '\n')
    
    t = ExerciseSet('E1',24)
    t.setShortNote('15kg')
    t.appendDescription(['Step 1','Step 2','Step 3'])

    t.scale(2)

    print(t)
