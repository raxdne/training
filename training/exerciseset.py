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

    def __init__(self,t,iArg=1):

        """  """

        super().__init__(t)

        self.repetitions = iArg
        self.img = []
        self.strNote = ''


    def __repr__(self):

        strResult = f'{self.__class__.__name__}({self.title!r})'
        if self.hasDescription():
            strResult += f'.appendDescription({self.description!r})'

        return strResult


    def __len__(self):

        return len(self.child)


    def __str__(self):

        return f'{self.repetitions} x {self.title} {self.strNote}'


    def set(self,**kwargs):
        
        """ generic setter """
        
        for key, value in kwargs.items():
            if key in ['dt','description','repetitions','d']:
                setattr(self, key, value)

        return self


    def getRepetitions(self):

        """ legacy """
        
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
        
        self.set(strNote=strArg)
                
        return self


    def toStringShort(self):

        """  """

        return str(self) + self.getDescriptionString()


    def toCSV(self):

        """  """

        strResult = ''
        for u in self.child:
            strResult += str(u) + ', '

        return strResult


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
            strResult += '<td>' + self.title + ' ' + self.strNote + '</td><td>' + str(self.repetitions) + '</td>'
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


    def to_ical(self,cal):

        """  """
        
        pass
    
    
    def toSqlite(self):

        """  """

        strResult = ''

        return strResult


    def stat(self, skipType=None):

        """  """

        listResult = []
        
        #listResult = [[self.dt.toordinal(), self.dist, self.getDuration().total_seconds() / 60, self.type]]

        return listResult


    def scale(self,f,p=None):

        """ returns a scaled copy of self """

        r = self.dup()
        if f > 0.01 and  abs(f - 1.0) > 0.01:
            r.repetitions = round(r.repetitions * f)

        return r


if __name__ == '__main__':

    print('Module Test: ' + __file__ + '\n')
    
    t = ExerciseSet('E1',24)
    t.setShortNote('15kg')
    t.appendDescription(['Step 1','Step 2','Step 3'])

    t.scale(2)

    print(t)
