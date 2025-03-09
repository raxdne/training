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
from training.pause import Pause

#
#
#

class Combination(Title,Note):

    def __init__(self,listArg=[],flagAnd=True):

        """  """

        Title.__init__(self)
        Description.__init__(self)
        
        self.child = []
        self.logicAnd = flagAnd
        self.dt = None

        for objArg in listArg:
            if objArg is None or (type(objArg) != Unit and type(objArg) != Pause and type(objArg) != Note and type(objArg) != Combination):
                print('error: ' + str(objArg), file=sys.stderr)
            else:
                self.child.append(objArg.dup())


    def __str__(self):

        """  """

        if self.logicAnd:
            strResult = 'Combination '
        else:
            strResult = 'Alternatives '

        strResult += self.getDuration().toString() + ' ' + self.getTitleString() + ' ' + self.getDescriptionString() + '\n'

        for u in self.child:
            strResult += '\t + ' + str(u) + '\n'
        strResult += '\n'

        return strResult


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
            if u.dt is None or (dt0 is not None and u.dt.date() < dt0) or (dt1 is not None and dt1 < u.dt.date()):
                # u is out of interval
                pass 
            elif type(u) is Unit and u.isCountable():
                intResult += 1

        return intResult


    def getRepresentativeAlternative(self):

        """ return the representative Unit of this combination (longest duration) """

        r = None

        if not self.logicAnd:
            s_max = 0
            for u in self.child:
                if type(u) is Unit:
                    s = u.getDuration().total_seconds()
                    if s > s_max:
                        r = u
                        s_max = s
                elif type(u) is Combination:
                    q = u.getRepresentativeAlternative()
                    s = q.getDuration().total_seconds()
                    if s > s_max:
                        r = q
                        s_max = s

        return r


    def getDuration(self):

        """ return a timedelta """

        intResult = 0
        if self.logicAnd:
            for u in self.child:
                if type(u) is Combination or type(u) is Unit:
                    intResult += u.getDuration().total_seconds()
        else:
            # Alternatives
            intResult = self.getRepresentativeAlternative().getDuration().total_seconds()

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

        if self.logicAnd:
            for u in self.child:
                if type(u) is Combination or (type(u) is Unit and u.isCountable()):
                    listResult.extend(u.stat())
        else:
            # stat longest unit of alternatives only
            m = self.getRepresentativeAlternative()
            if m is not None:
                listResult.extend(m.stat())

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
            strResult += '/>'

            if self.logicAnd:
                strResult += 'Combination: ' + self.getDuration().toString()
            else:
                strResult += 'Alternatives: max. ' + self.getDuration().toString()

            strResult += self.getDescriptionString() + '</div>'

            if self.logicAnd:
                strResult += '<ol>'
            else:
                strResult += '<ol style="list-style-type: lower-latin">'

            for u in self.child:
                strResult += '<li>' + u.toHtmlTable() + '</li>'
            strResult += '</ol>'
        elif self.child:
            strResult = '<div>' + self.child[0].toHtmlTable() + '</div>'

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
            if self.logicAnd:
                for u in self.child:
                    u.to_ical(cal)
            else:
                event = Event()
                m = self.getRepresentativeAlternative()

                if m is not None and not (m.dt is None and m.tPlan is None) and cal is not None and event is not None:
                    event.add('summary', f'Alternatives: {self.toStringShort()}')
                    event.add('dtstamp', datetime.now().astimezone(None))
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

