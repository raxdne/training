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

import copy

from datetime import timedelta, date, datetime, time

from icalendar import Calendar, Event, Alarm

from training import config as config
from training.duration import Duration
from training.description import Description
from training.title import Title
from training.note import Note
from training.unit import Unit
from training.exerciseset import ExerciseSet
from training.pause import Pause

#
#
#

class Combination(Title,Note):

    def __init__(self,listArg=[],flagAnd=True):

        """  """

        super(Title, self).__init__()
        super(Note, self).__init__()

        self.setDescription()
        
        self.child = []
        self.logicAnd = flagAnd
        self.dt = None

        for objArg in listArg:
            if objArg is None or (type(objArg) != Unit and type(objArg) != ExerciseSet and type(objArg) != Pause and type(objArg) != Note and type(objArg) != Combination):
                print('error: ' + str(objArg), file=sys.stderr)
            else:
                self.child.append(objArg.dup())


    def __str__(self):

        """  """

        if self.isCircuit():
            strResult = 'Circuit '
        elif self.logicAnd:
            strResult = 'Combination '
        else:
            strResult = 'Alternatives '

        strResult += self.getDuration().toString() + ' ' + self.getTitleString() + ' ' + self.getDescriptionString() + '\n'

        for u in self.child:
            strResult += '\t + ' + str(u) + '\n'
        strResult += '\n'

        return strResult


    def isCircuit(self):

        """  """

        for i in range(len(self.child)):
            if type(self.child[i]) is Combination or type(self.child[i]) is ExerciseSet or type(self.child[i]) is Pause:
                pass
            else:
                return False
            
        return True


    def toStringShort(self):

        """  """

        # common date
        strDate = ''

        strResult = ''

        for i in range(len(self.child)):
            if type(self.child[i]) is Note:
                pass
            else:
                if i < 1:
                    pass
                elif self.logicAnd:
                    # Combination
                    strResult += ' & '
                else:
                    # Alternatives
                    strResult += ' | '
                strResult += self.child[i].toStringShort()

                if not strDate and type(self.child[i]) is Unit and self.child[i].dt is not None:
                    strDate = self.child[i].dt.strftime("%Y-%m-%d ")

        return f'({strResult} {self.getTitleString()} {self.getDescriptionString()})'


    def setDate(self,dtArg=None,dt_0=None,dt_1=None):

        """ fix 'dt' according to sunrise/sunset """

        #print(__name__ + ': ' + str(self), file=sys.stderr)

        if dtArg is None:
            return None
        elif type(dtArg) is date:
            return self.setDate(datetime.combine(dtArg,time(0)).astimezone(None),dt_0,dt_1)
        elif not self.logicAnd:
            m = self.getRepresentativeAlternative()
            if m is not None:
                dt = m.setDate(dtArg)
        else:
            i = 0
            self.dt = dtArg
            dt = self.dt
            for u in self.child:
                
                if type(u) is Note:
                    u.setDate(dt)
                elif type(u) is Combination:
                    u.setDate(dt)
                    i += 1
                elif type(u) is ExerciseSet:
                    u.setDate(dt)
                    i += 1
                elif type(u) is Unit:

                    if i == 0:
                        # initial unit
                        if u.tPlan is None:
                            #dt = dt_0
                            pass
                        elif type(u.tPlan) is str and u.tPlan == 'sunrise' and dt_0 is not None:
                            # shift start time after twilight
                            dt = dt_0
                            dt += timedelta(minutes=(dt.minute % 15))
                        elif type(u.tPlan) is str and u.tPlan == 'sunset' and dt_1 is not None:
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
                    dt = u.setDate(dt)
                    i += 1
                
        return dt


    def updateValues(self,dictArg=None):

        """  """

        if dictArg is not None:
            for c in self.child:
                if type(c) is Unit:
                    c.updateValues(dictArg)

        return self


    def remove(self,patternType=None):

        """  """

        if patternType is not None:
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


    def append(self,objArg):

        """  """
        
        if type(objArg) is list:
            for e in objArg:
                self.child.append(e)
        else:
            self.child.append(objArg)
        
        return self


    def resetDistances(self):

        """  """

        for u in self.child:
            if type(u) is Unit:
                u.setDistStr(None)

        return self


    def getNumberOfUnits(self, dt0=None, dt1=None):

        """  """

        intResult = 0

        for u in self.child:
            if u.dt is not None and ((dt0 is not None and u.dt.date() < dt0) or (dt1 is not None and dt1 < u.dt.date())):
                # u is out of interval
                pass 
            elif type(u) is Unit and u.isCountable():
                intResult += 1

        return intResult


    def getRepresentativeAlternative(self, skipType=None):

        """ return the representative Unit of this combination (longest duration) """

        r = None

        if not self.logicAnd:
            s_max = 0
            for u in self.child:
                if type(u) is Unit:
                    s = u.getDuration(skipType).total_seconds()
                    if s > s_max:
                        r = u
                        s_max = s
                elif type(u) is Combination:
                    q = u.getRepresentativeAlternative(skipType)
                    s = q.getDuration().total_seconds()
                    if s > s_max:
                        r = q
                        s_max = s

        return r


    def getDuration(self, skipType=None):

        """ return a timedelta """

        intResult = 0
        if self.logicAnd:
            for u in self.child:
                if type(u) is Combination or type(u) is Unit or type(u) is ExerciseSet or type(u) is Pause:
                    intResult += u.getDuration(skipType).total_seconds()
        else:
            # Alternatives
            intResult = self.getRepresentativeAlternative(skipType).getDuration().total_seconds()

        return Duration(intResult / 60)


    def scale(self,floatScale,patternType=None):

        """  """

        r = self.dup()
        if floatScale > 0.01 and  abs(floatScale - 1.0) > 0.01:
            for u in r.child:
                if type(u) is Unit or type(u) is ExerciseSet:
                    u.scale(floatScale,patternType)

        return r


    def stat(self, skipType=None):

        """  """

        listResult = []

        if self.logicAnd:
            for u in self.child:
                if type(u) is Combination or type(u) is ExerciseSet or (type(u) is Unit and u.isCountable()):
                    listResult.extend(u.stat(skipType))
        else:
            # stat longest unit of alternatives only
            m = self.getRepresentativeAlternative()
            if m is not None:
                listResult.extend(m.stat(skipType))

        return listResult


    def dup(self):

        """  """

        return copy.deepcopy(self)


    def toHtmlTable(self):

        """  """

        strResult = ''

        if len(self.child) > 1:
            strResult = '<div'
            if self.color is not None:
                strResult += ' style="background-color: {}"'.format(self.color)
            strResult += '>'

            if self.hasTitle():
                strResult += self.getTitleString() + ' ' + self.getDuration().toString()
            elif self.isCircuit():
                strResult += 'Circuit: ' + self.getDuration().toString()
            elif self.logicAnd:
                strResult += 'Combination: ' + self.getDuration().toString()
            else:
                strResult += 'Alternatives: max. ' + self.getDuration().toString()

            strResult += self.getDescriptionHTML()

            if self.logicAnd:
                strResult += '<ol style="margin-block-start: 2px; margin-block-end: 2px;">'
            else:
                strResult += '<ol style="list-style-type: lower-latin; margin-block-start: 2px; margin-block-end: 2px;">'

            for u in self.child:
                strResult += '<li>' + u.toHtmlTable() + '</li>'
            strResult += '</ol>' + '</div>'
        elif self.child:
            strResult = '<div>' + self.child[0].toHtmlTable() + '</div>'

        return strResult


    def toHtmlSheet(self,fImages=False):

        """  """

        strResult = ''

        if len(self.child) > 0:
            strResult = '<table'
            if self.color is not None:
                strResult += ' style="background-color: {}"'.format(self.color)
            strResult += '>'

            #strResult += '<thead><tr><th>#</th><th>Name</th><th>Count</th><th>Description</th><th>Picture</th></tr></thead>'

            strResult += '<tbody>'

            if self.hasTitle():
                strResult += '<tr><th colspan="4">' + self.getTitleString() + '</th></tr>'

            #strResult += self.getDescriptionHTML()

            for u in self.child:
                if type(u) is Combination:
                    strResult += '<tr><td>' + u.toHtmlSheet(fImages) + '</td></tr>'
                elif type(u) is ExerciseSet:
                    strResult += u.toHtmlSheet(fImages)
                else:
                    strResult += '<tr><td>' + u.toHtmlTable() + '</td></tr>'
                
            strResult += '</tbody>'
            strResult += '</table>'
        #elif self.child:
        #    strResult = '<div>' + self.child[0].toHtmlTable() + '</div>'

        return strResult


    def toHtmlFile(self,fImages=False):

        """ returns html/body + content """

        strResult = '<!doctype html public "-//IETF//DTD HTML 4.0//EN">'

        strResult += "<html>"

        strResult += "<head>"

        strResult += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>'

        strResult += "<title></title>"

        strResult += config.style

        strResult += config.script

        strResult += "</head>"

        strResult += "<body>" + self.toHtmlSheet(fImages) + "</body>"

        strResult += "</html>"

        return strResult


    def toCSV(self):

        """  """

        # TODO: if self.logicAnd:

        strResult = ''
        for u in self.child:
            strResult += u.toCSV()

        return strResult


    def toSVG(self,x,y):

        """  """

        strResult = '<g>'

        x_i = x
        if self.logicAnd:
            for u in self.child:
                if type(u) is Unit or type(u) is Pause:
                    strResult += u.toSVG(x_i,y)
                    x_i += u.getDuration().total_seconds() / 3600 * 25 * config.diagram_scale_dist
        else:
            m = self.getRepresentativeAlternative()
            if m is not None:
                strResult += m.toSVG(x_i,y)
                x_i += m.getDuration().total_seconds() / 3600 * 25 * config.diagram_scale_dist
             
        strResult += '</g>'

        return strResult


    def toFreemindNode(self):

        """  """

        strResult = ''

        if len(self.child) > 1:
            strResult = '<node'
            if self.color is not None:
                strResult += f' BACKGROUND_COLOR="{self.color}"'
            elif self.getNumberOfUnits() < 1:
                strResult += f' BACKGROUND_COLOR="#ffaaaa"'
            else:
                strResult += f' FOLDED="true"'

            if self.logicAnd:
                strResult += ' TEXT="Combination ' + self.getDuration().toString() + '"'
            else:
                strResult += ' TEXT="Alternatives"'
            strResult += '>\n'

            strResult += self.getDescriptionFreemind()

            for u in self.child:
                strResult += u.toFreemindNode()
                            
            strResult += '</node>\n'
        elif self.child:
            # only a single child
            strResult += self.child[0].toFreemindNode()

        return strResult


    def to_ical(self,cal=None):

        """  """
        
        if len(self.child) > 1:
            event = Event()
            event.add('dtstamp', datetime.now().astimezone(None))
            if self.logicAnd:
                m = self.child[0]
                event.add('summary', f'Combination: {self.toStringShort()}')
                if m.dt is None and m.tPlan is not None:
                    # no day defined
                    dt = datetime.combine(date.today(), m.tPlan)
                    event.add('dtstart', dt)
                    event.add('dtend', dt + self.getDuration())
                elif m.dt is None:
                    # no day defined
                    pass
                elif type(m.tPlan) is datetime.time:
                    # day defined
                    dt = datetime.combine(m.dt, m.tPlan)
                    event.add('dtstart', dt)
                    event.add('dtend', dt + self.getDuration())
                elif m.dt.time() == time(0) or self.getDuration() is None:
                    # no time defined
                    event.add('dtstart', m.dt.date())
                    event.add('dtend', m.dt.date() + timedelta(days=1))
                else:
                    event.add('dtstart', m.dt)
                    event.add('dtend', m.dt + self.getDuration())

                cal.add_component(event)

            else:
                m = self.getRepresentativeAlternative()

                if m is not None and not (m.dt is None and m.tPlan is None) and cal is not None and event is not None:
                    event.add('summary', f'Alternatives: {self.toStringShort()}')
                    if m.dt is None and m.tPlan is not None:
                        # no day defined
                        dt = datetime.combine(date.today(), m.tPlan)
                        event.add('dtstart', dt)
                        event.add('dtend', dt + m.duration)
                    elif m.tPlan is not None:
                        # day defined
                        dt = datetime.combine(m.dt, m.tPlan)
                        event.add('dtstart', dt)
                        event.add('dtend', dt + m.duration)
                    elif m.dt.time() == time(0) or m.duration is None:
                        # no time defined
                        event.add('dtstart', m.dt.date())
                        event.add('dtend', m.dt.date() + timedelta(days=1))
                    else:
                        event.add('dtstart', m.dt)
                        event.add('dtend', m.dt + m.duration)

                    cal.add_component(event)
                else:
                    print('error: ' + 'not defined', file=sys.stderr)
        elif self.child:
            # only a single child
            self.child[0].to_ical(cal)

