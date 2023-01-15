#
# Data Management for Physical Training
#
# Copyright (C) 2021,2022 by Alexander Tenbusch
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

#
#
#

class Combination(Title,Description):

    def __init__(self,listArg=[]):

        """  """

        super(Title, self).__init__()
        super(Description, self).__init__()
        
        self.child = []

        for c in listArg:
            self.child.append(c.dup())


    def __str__(self):

        """  """

        strResult = 'Combination: '
        strResult += super().__listDescriptionToString__() + '\n'

        for u in self.child:
            strResult += '\t' + str(u) + '\n'
        strResult += '\n'

        return strResult


    def appendDescription(self,objArg):

        """  """

        super().appendDescription(objArg)

        return self


    def setDate(self,dateArg):

        """  """

        if dateArg != None:
            
            dt = dateArg
            for u in self.child:

                if u.clock != None:
                    dt = datetime.combine(date(dateArg.year,dateArg.month,dateArg.day),u.clock)

                u.dt = dt

                if type(u) == Unit or type(u) == Pause:
                    dt += u.duration
            
        return True


    def setDistStr(self,strArg):

        """  """


    def resetDistances(self):

        """  """

        for u in self.child:
            if type(u) == Unit:
                u.setDistStr(None)

        return self


    def getNumberOfUnits(self):

        """  """

        intResult = 0

        for u in self.child:
            if type(u) == Unit and u.type != None and len(u.type) > 0:
                intResult += 1

        return intResult


    def getDuration(self):

        """ return a timedelta """

        intResult = 0
        for u in self.child:
            if (type(u) == Unit or type(u) == Pause):
                intResult += u.getDuration().total_seconds()

        return timedelta(seconds=intResult)


    def getTypeOfUnits(self,arrArg=None):

        """  """

        if arrArg == None:
            arrArg = []

        for v in self.child:
            for u in v:
                if type(u) == Unit and u.type != None and len(u.type) > 0:
                    if u.type in arrArg:
                        pass
                    else:
                        arrArg.append(u.type)

        return arrArg


    def scale(self,floatScale,patternType=None):

        """  """

        for v in self.child:
            for u in v:
                if type(u) == Unit:
                    u.scale(floatScale,patternType)

        return self


    def stat(self, dictArg):

        """  """

        if dictArg == None:
            print('error: ' + 'no dict', file=sys.stderr)
        else:
            for u in self.child:
                if type(u) == Unit:
                    u.stat(dictArg)


    def dup(self):

        """  """

        return copy.deepcopy(self)


    def toHtml(self):

        """  """
        
        strResult = '<section class="{}"'.format(__name__)

        if self.color != None:
            strResult += ' style="background-color: {}"'.format(self.color)

        strResult += '>\n<ul>' + super().__listDescriptionToHtml__() + '</ul>'

        for u in self.child:
            strResult += u.toHtml()
        
        strResult += '</section>'

        return strResult


    def toCSV(self):

        """  """

        strResult = '\n* ' + self.getTitleStr() + ' (' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n'
        for v in self.child:
            for u in v:
                if type(u) == Unit:
                    strResult += u.toCSV() + '\n'

        return strResult


    def toSVG(self,x,y):

        """  """

        strResult = '<g>'

        x_i = x
        for u in self.child:
            strResult += u.toSVG(x_i,y)
            x_i += u.getDuration().total_seconds() / 3600 * 25 * config.diagram_scale_dist
             
        strResult += '</g>'

        return strResult


    def toXML(self):

        """  """

        strResult = '<node'

        if self.color != None:
            strResult += ' BACKGROUND_COLOR="{}"'.format(self.color)
        elif self.getNumberOfUnits() < 1:
            strResult += ' BACKGROUND_COLOR="{}"'.format('#ffaaaa')
        else:
            strResult += ' FOLDED="{}"'.format('true')

        strResult += ' TEXT="' + self.child[0].dt.isoformat() + '">\n'

        strResult += self.__listDescriptionToXML__()

        for u in self.child:
            strResult += u.toXML()
                        
        strResult += '</node>\n'

        return strResult


    def to_ical(self,cal):

        """ 

        event = Event()
        event.add('summary', 'Combination: {}'.format(str(self)))
        event.add('dtstart', self.dateBegin)
        event.add('dtend', self.dateEnd + timedelta(days=1))
        event.add('dtstamp', datetime.now().astimezone(None))
        cal.add_component(event)
        """
        
        for u in self.child:
            u.to_ical(cal)


