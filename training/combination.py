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
from training.duration import Duration
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

        Title.__init__(self)
        Description.__init__(self)
        
        self.child = []

        for objArg in listArg:
            if objArg == None or (type(objArg) != Unit and type(objArg) != Pause and type(objArg) != Note):
                print('error: ' + str(objArg), file=sys.stderr)
            else:
                self.child.append(objArg.dup())


    def __str__(self):

        """  """

        strResult = 'Combination: {} {} {}\n'.format(self.getDuration().toString(), self.getTitleString(), self.getDescriptionString())
        for u in self.child:
            strResult += '\t + ' + str(u) + '\n'
        strResult += '\n'

        return strResult


    def setDate(self,dtArg=None,dt_0=None,dt_1=None):

        """ fix 'dt' according to sunrise/sunset """

        #print(__name__ + ': ' + str(self), file=sys.stderr)

        if dtArg == None:
            return None
        elif type(dtArg) is date:
            return self.setDate(datetime.combine(dtArg,time(0)).astimezone(None),dt_0,dt_1)
        else:
            i = 0
            dt = dtArg
            for u in self.child:
                
                if type(u) is Note:
                    u.setDate(dt)
                elif type(u) is Unit:

                    if i == 0:
                        # initial unit
                        if u.tPlan == None:
                            #dt = dt_0
                            pass
                        elif type(u.tPlan) is str and u.tPlan == 'sunrise' and dt_0 != None:
                            # shift start time after twilight
                            dt = dt_0
                            dt += timedelta(minutes=(dt.minute % 15))
                        elif type(u.tPlan) is str and u.tPlan == 'sunset' and dt_1 != None:
                            # shift end time before twilight
                            dt = dt_1 - self.getDuration()
                            dt -= timedelta(minutes=(dt.minute % 15))
                        elif type(u.tPlan) is time:
                            dt = datetime.combine(dtArg.date(),u.tPlan).astimezone(None)
                        else:
                            #dt = datetime.combine(dtArg.date(),u.tPlan).astimezone(None)
                            dt = dtArg
                                
                        #print(__name__ + ': set start to ' + str(dt), file=sys.stderr)
                        
                    dt = u.setDate(dt)
                    i += 1
                elif type(u) is Pause:
                    if i == 0:
                        print(__name__ + ': ignoring initial' + str(self), file=sys.stderr)
                    else:
                        dt = u.setDate(dt)
                        i += 1
                
        return dt


    def remove(self,patternType=None):

        """  """

        if patternType != None:
            # whole combination using pattern
            childsNew = []
            for u in self.child:
                if type(u) is Unit and u.match(patternType):
                    pass
                elif type(u) is Pause:
                    pass
                else:
                    childsNew.append(u)
                    
            self.child = childsNew
            
        return self


    def resetDistances(self):

        """  """

        for u in self.child:
            if type(u) is Unit:
                u.setDistStr(None)

        return self


    def getNumberOfUnits(self):

        """  """

        intResult = 0

        for u in self.child:
            if type(u) is Unit and u.isCountable():
                intResult += 1

        return intResult


    def getDuration(self):

        """ return a timedelta """

        intResult = 0
        for u in self.child:
            if ((type(u) is Unit and u.isCountable()) or type(u) is Pause):
                intResult += u.getDuration().total_seconds()

        return Duration(intResult / 60)


    def scale(self,floatScale,patternType=None):

        """  """

        for u in self.child:
            if type(u) is Unit:
                u.scale(floatScale,patternType)

        return self


    def stat(self):

        """  """

        listResult = []

        for u in self.child:
            if type(u) is Unit and u.isCountable():
                listResult.extend(u.stat())

        return listResult


    def dup(self):

        """  """

        return copy.deepcopy(self)


    def toHtml(self):

        """  """
        
        strResult = '<section class="{}"'.format(__name__)

        if self.color != None:
            strResult += ' style="background-color: {}"'.format(self.color)

        strResult += '>\n<ul>' + self.getDescriptionHTML() + '</ul>'

        for u in self.child:
            strResult += u.toHtml()
        
        strResult += '</section>'

        return strResult


    def toHtmlTable(self):

        """  """

        strResult = '<div>' + 'Combination: {} {}\n'.format(Duration(self.getDuration()), self.getDescriptionString()) + '</div>'
        strResult += '<ol>'
        for u in self.child:
            strResult += '<li>' + u.toHtmlTable() + '</li>'
        strResult += '</ol>'

        return strResult


    def toCSV(self):

        """  """

        strResult = ''
        for u in self.child:
            strResult += u.toCSV()

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


    def toFreemindNode(self):

        """  """

        strResult = '<node'

        if self.color != None:
            strResult += ' BACKGROUND_COLOR="{}"'.format(self.color)
        elif self.getNumberOfUnits() < 1:
            strResult += ' BACKGROUND_COLOR="{}"'.format('#ffaaaa')
        else:
            strResult += ' FOLDED="{}"'.format('true')

        strResult += ' TEXT="Combination">\n'

        strResult += self.getDescriptionFreemind()

        for u in self.child:
            strResult += u.toFreemindNode()
                        
        strResult += '</node>\n'

        return strResult


    def to_ical(self,cal):

        """  """
        
        for u in self.child:
            u.to_ical(cal)


