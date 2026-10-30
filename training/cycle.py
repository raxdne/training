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
from training.tcontainer import TContainer
from training.titem import TItem

from training.note import Note
from training.unit import Unit
from training.pause import Pause
from training.combination import Combination
from training.exerciseset import ExerciseSet
from training.plot import Plot

#
#
#

class Cycle(TContainer):

    def __init__(self,t=None,l=7):

        """  """

        super().__init__(t,l)

        for i in range(int(l)):
            self.child.append([]) # to get independant instances

        return


    def __str__(self):

        strResult = super().__str__()

        for v in self.child:
            for u in v:
                if isinstance(u,Unit) or isinstance(u,Combination):
                    strResult += f'{u}\n'

        return strResult


    def set(self,**kwargs):
        
        """ generic setter """
        
        for key, value in kwargs.items():
            if key in ['color','description','title']:
                setattr(self, key, value)

        return self


    def getLength(self):

        """ return length of cycle """

        return len(self.child)


    def append(self,o):

        """ append objects to the list of childs """

        self.clean()

        if o is None:
            print('error: ' + str(o), file=sys.stderr)
        elif isinstance(o,list):
            for a in o:
                self.append(a)
        elif isinstance(o,Cycle):
            self.child.extend(o.child)
            self.setPeriod(len(self.child))
        elif isinstance(o,Unit) or isinstance(o,Note):
            self.child.extend([[]])
            self.child[-1].append(o.dup())
            self.setPeriod(len(self.child))
        else:
            print('error: ' + str(o), file=sys.stderr)

        return self


    def schedule(self, argDateOrYear=None, intMonth=None, intDay=None):

        """  """

        super().schedule(argDateOrYear, intMonth, intDay)
        
        dt_earliest = None
        dt_latest   = None
        dt_i = datetime.combine(self.dateBegin,time(0)).astimezone(None)

        for d in self.child:

            if config.sun is not None:
                # fix 't' according to sunrise/sunset
                dt_earliest = config.sun.get_local_sunrise_time(dt_i) + timedelta(seconds=config.twilight)
                dt_latest   = config.sun.get_local_sunset_time(dt_i)  - timedelta(seconds=config.twilight)

            for t in d:
                t.setDate(dt_i,dt_earliest,dt_latest)

            dt_i += timedelta(days=1)

        return self


    def updateValues(self,dictArg=None):

        """  """

        if dictArg is not None:
            self.setVDefaults(dictArg)

        for v in self.child:
            for u in v:
                if isinstance(u,Unit) or isinstance(u,Combination):
                    u.updateValues(self.v_defaults)

        return self


    def resetDistances(self):

        """  """

        self.clean()

        for i in range(len(self.child)):
            self.child[i] = []

        return self


    def remove(self,a=-1,p=None):

        """ BUG: removal of matching units in Combination() """

        if a > -1 and a < len(self.child):
            if p is not None:
                # delete only matching elements in list of indexed day
                dayNew = []
                for u in self.child[a]:
                    if isinstance(u,Combination):
                        c = u.remove(p)
                        if c.getNumberOfUnits() > 0:
                            daysNew.append(c)
                    elif isinstance(u,Unit) and u.match(p):
                        # to be ignored
                        pass
                    else:
                        dayNew.append(u.dup())
                self.child[a] = copy.deepcopy(dayNew)
            else:
                # delete whole list of indexed day
                self.child[a].clear()
        elif p is not None:
            # whole cycle using pattern
            daysNew = []
            for i in range(0,len(self.child)):
                daysNew.append([])
                for u in self.child[i]:
                    if isinstance(u,Combination):
                        c = u.remove(p)
                        if c.getNumberOfUnits() > 0:
                            daysNew[i].append(c)
                    elif isinstance(u,Unit) and u.match(p):
                        # to be ignored
                        pass
                    else:
                        daysNew[i].append(u)
            self.child = daysNew

        return self


    def shift(self,a,b=None,f=False):

        """  """

        if type(a) != int:
            print('error: shift of a cycle requires an integer value', file=sys.stderr)
        elif b is None:
            # shift
            print('info: shift by ' + str(a), file=sys.stderr)
            if a > 0 and a < len(self.child):
                for i in range(0,a):
                    self.child.insert(0,[])
                for i in range(0,a):
                    self.child.pop()
            elif a < 0 and a > - len(self.child):
                for i in range(0, - a):
                    self.child.pop(0)
                for i in range(0, - a):
                    self.child.append([])
        elif type(b) != int:
            print('error: shift of a cycle requires an integer value', file=sys.stderr)
        elif a > -1 and b > -1 and a < len(self.child) and b < len(self.child) and a != b:
            self.copy(a,b,f)
            self.remove(a)

        return self


    def insert(self,n,o,f=False):

        """  """

        objResult = self
        j = len(self.child)

        if o is None:

            print('error: undefined object ' + str(o), file=sys.stderr)

        elif type(n) is list and n:

            for i in n:
                self.insert(i,o,f)

        elif isinstance(o,list) and o:

            for u in o:
                self.insert(n,u,f)

        elif type(n) is int and n > -1 and n < j and isinstance(o,TItem):

            if f:
                # overwrite existing
                self.child[n] = [o.dup()]
            else:
                self.child[n].append(o.dup())

            if self.dateBegin is not None:
                self.schedule(self.dateBegin)

        elif type(n) is int and n > -1 and n < j and isinstance(o,Cycle) and len(o.child) > 0:

            for i in range(o.getLength()):
                k = n + i
                if k == j:
                    break
                #elif isinstance(o.child[i],Note):
                #    self.insert(k,u,f)
                elif len(o.child[i]) < 1:
                    self.child[k].clear()
                else:
                    for u in o.child[i]:
                        self.insert(k,u,f)
                i += 1

        else:
            print(f'error: inserting {type(o)} at position {n} of {j} {o}', file=sys.stderr)

        return objResult


    def fill(self,o,s=1.0):

        """ progression s """

        f=False
        objResult = self

        if o is None:

            print('error: undefined object ' + str(o), file=sys.stderr)

        elif type(o) is list and o:

            for u in o:
                self.insert(u,f)

        elif isinstance(o,Unit) or isinstance(o,Combination) or isinstance(o,Note):

            i = 0
            for v in o.child:
                for u in v:
                    self.insert(i,u,f)
                i += 1

        elif isinstance(o,Cycle) and o.child:

            i = 0
            d = len(self.child)
            b = len(o.child)
            while i < d:
                j = 0
                while j < b and i < d:
                    if o.child[j]:
                        for u in o.child[j]:
                            self.insert(i,u,f)
                    elif f:
                        self.child[i].clear()
                    i += 1
                    j += 1
                o.scale(s)

        else:
            print(f'error: filling {type(o)} of {len(self.child)} {o}', file=sys.stderr)

        return objResult


    def overwrite(self,c,d=None):

        """ overwrite the descendant cycle sequence by c """

        if isinstance(c,Cycle) and d is not None and isinstance(d,date):
            self.insert((d - self.dateBegin).days,c,True)
        elif isinstance(c,Cycle) and c.dateBegin:
            self.overwrite(c,c.dateBegin)
        else:
            print(f'error: inserting {type(c)} at date {d}', file=sys.stderr)

        return self


    def insertByDate(self,o,f=False):

        """ returns a reference to an object which was inserted according its date """

        objResult = None

        if o is None or o.dt is None:
            print('error: undefined ' + str(o), file=sys.stderr)
        elif self.dateBegin is None:
            print('error: date begin', file=sys.stderr)
        elif isinstance(o,TItem):
            delta = o.dt.date() - self.dateBegin
            if delta.days < 0 or delta.days >= len(self.child):
                pass
            elif o.dt.date() <= self.dateEnd:
                #print(f'info: inserting {type(o)} at position {delta.days} of {len(self.child)} {o}', file=sys.stderr)
                objResult = o.dup()
                if f:
                    # overwrite existing
                    self.child[delta.days] = [objResult]
                else:
                    self.child[delta.days].append(objResult)

        return objResult


    def stretch(self,n=1,m=1):

        """ insert every n-th day m extra days """

        if type(n) is int and n > 0 and len(self.child) > n:

            d = []
            for i in range(len(self.child)):
                d.append(self.child[i])
                if i % n == 0:
                    for j in range(m):
                        d.append([])

            self.child = d

        return self


    def extend(self,n=7):

        """ append last n days at the end """

        if type(n) is int and n > 0 and len(self.child) >= n:
            self.child.extend(copy.deepcopy(self.child[-n:]))

        return self


    def cutBefore(self,d):

        """  """

        assert type(d) is date

        if self.dateBegin < d and d <= self.dateEnd:
            delta = (d - self.dateBegin).days
            if delta > 0:
                del self.child[:delta]
                self.clean()
                self.schedule(d)

        return self


    def cutAfter(self,d):

        """  """

        assert type(d) is date

        if self.dateBegin <= d and d < self.dateEnd:
            delta = (d - self.dateBegin).days
            if delta > -1:
                self.clean()
                del self.child[delta+1:]
                self.schedule(self.dateBegin)

        return self


    def getPeriodDone(self):

        """  """

        if not self.fPlan and self.dateBegin is not None and date.today() >= self.dateBegin and self.dateEnd is not None and date.today() <= self.dateEnd:
            return (date.today() - self.dateBegin).days + 1
        else:
            return (self.dateEnd - self.dateBegin).days + 1


    def getNumberOfUnits(self, dt0=None, dt1=None):

        """  """

        # TODO: use self.data

        intResult = 0
        for v in self.child:
            for u in v:
                if u.dt is not None and ((dt0 is not None and u.dt.date() < dt0) or (dt1 is not None and dt1 < u.dt.date())):
                    # u is out of interval
                    pass 
                elif isinstance(u,Combination):
                    intResult += u.getNumberOfUnits(dt0,dt1)
                elif isinstance(u,Unit) and u.isCountable():
                    intResult += 1

        return intResult


    def getMarkers(self, dt0=None, dt1=None):

        """  """

        listResult = []
        for v in self.child:
            for u in v:
                if u.dt is not None and ((dt0 is not None and u.dt.date() < dt0) or (dt1 is not None and dt1 < u.dt.date())):
                    # u is out of interval
                    pass 
                elif isinstance(u,Combination) and u.isMarked():
                    listResult.append(u)
                elif isinstance(u,Unit) and u.isMarked():
                    listResult.append(u)

        return listResult


    def getItem(self,index):

        """ return item of index in cycle """

        if type(index) is int:
            if index < len(self.child):
                return self.child[index]
            else:
                return self.child[-1]
        elif type(index) is list:
            if len(index) == 1:
                return self.getItem(index[0])
            elif len(index) > 1:
                if index[0] < len(self.child):
                    if index[1] < len(self.child[index[0]]):
                        return self.child[index[0]][index[1]]
                    elif len(self.child[index[0]]) > 0:
                        return self.child[index[0]][-1]
    
        return None


    def getDuration(self, skipType=None):

        """ return a timedelta """

        # TODO: use self.data

        if skipType is None:
            skipType = self.skipType

        intResult = 0
        for v in self.child:
            for u in v:
                if (isinstance(u,Unit) and u.isCountable()) or isinstance(u,Combination):
                    intResult += u.getDuration(skipType).total_seconds()

        return timedelta(seconds=intResult)


    def scale(self,f,p=None):

        """ returns a copy of self, scaled by f and matching pattern p if not None """

        r = self.dup()
        if f > 0.01 and abs(f - 1.0) > 0.01:
            for j in range(len(r.child)):
                for i in range(len(r.child[j])):
                    if type(r.child[j][i]) is Unit or type(r.child[j][i]) is ExerciseSet or type(r.child[j][i]) is Combination:
                        r.child[j][i] = r.child[j][i].scale(f,p)

        r.clean()

        return r


    def fix(self, o):

        """  """

        if self.dateFixed is not None:
            # keep fixed date
            pass
        #elif self.dateBegin is None or self.dateEnd is None:
        #    pass
        #elif o is not None and isinstance(o,date) and self.dateBegin <= o and o <= self.dateEnd:
        elif o is not None and isinstance(o,date):
            self.dateFixed = o
            self.dateBegin = self.dateFixed
            self.dateEnd = self.dateBegin + timedelta(days = len(self.child) - 1)

        return self


    def stat(self, dt0=None, dt1=None, skipType=None):

        """ stat all descendant data to self.data and returns it as a nested list  """

        if self.child:
            if skipType is None:
                skipType = self.skipType
            self.clean()
            for v in self.child:
                for u in v:
                    if u.dt is None or (dt0 is not None and u.dt.date() < dt0) or (dt1 is not None and dt1 < u.dt.date()):
                        # u is out of interval
                        pass 
                    elif (isinstance(u,Unit) and u.isCountable()) or isinstance(u,Combination):
                        self.data.extend(u.stat(skipType))

        return self.data


    def toHtmlTable(self):

        """  """

        strResult = f'<section {config.getClass(__name__)} id="{str(id(self))}"'

        if self.color is not None:
            strResult += ' style="background-color: {}"'.format(self.color)

        strResult += '><div class="header" ondblclick="removeDetails(this)">' + self.getTitleXML() + ' ' + self.getDateString() + '</div>\n'

        strResult += self.getDescriptionHTML()

        if self.getNumberOfUnits() > 0:
            strResult += f'<pre {config.getClass(__name__)}>' + self.report() + '</pre>'
            
        m = self.getMarkers()
        if len(m) > 0:
            strResult += '<p>Marked Units (Peaks)</p>'
            strResult += '<ol>'
            for u in m:
                strResult += f'<li>{u}</li>'
            strResult += '</ol>'

        if False and self.fPlot:
            strResult += '<div style="text-align: center;margin: 0px;">'
            #strResult += self.plotAccumulationDuration()
            #strResult += self.plotAccumulation()
            #strResult += self.plotHist()
            #strResult += self.plotTimeDist()
            #strResult += self.toSVGGanttChart()
            strResult += '</div>'
            strResult += self.toSVGDiagram()
        else:
            strResult += '<table>\n'

            strResult += '<colgroup><col span="1" style="width: 10%;"><col span="1" style="width: 90%;"></colgroup>\n'

            strResult += '<tbody>'
            dt_i = datetime.combine(self.dateBegin,time(0)).astimezone(None)
            for v in self.child:
                strResult += '<tr>'

                strResult += '<td'
                if dt_i.weekday() == 5 or dt_i.weekday() == 6:
                    strResult += ' class="we"'
                strResult += '>'

                #a = (not self.fPlan and len([u for u in v if isinstance(u,Unit)]) > 0)
                a = False
                
                strResult += '<div class="training-date">'
                if a:
                    # REQ: make link portable/configurable
                    strResult += '<a href="' + config.getURL(dt_i.strftime("%Y-%m-%d.*fitx")) + '">'
                strResult += dt_i.strftime("%Y-%m-%d %a (%j)")
                if a:
                    strResult += '</a>'
                strResult += '</div>'

                strResult += '</td>'

                strResult += '<td>'
                if v:
                    for u in v:
                        strResult += u.toHtmlTable()
                strResult += '</td>'
                strResult += '</tr>'
                dt_i += timedelta(days=1)

            strResult += '</tbody></table>'

        strResult += '</section>'

        return strResult

    # define simple Alias
    toHtml = toHtmlTable


    def toCSV(self):

        """  """

        strResult = '{};;;;Cycle "{}" {}\n'.format(self.dateBegin.strftime("%Y-%m-%d"), self.title, self.getDateString())
        for v in self.child:
            for u in v:
                strResult += u.toCSV()
        strResult += '\n'

        return strResult


    def toSqlite(self):

        """  """

        strResult = ''
        for v in self.child:
            for u in v:
                if isinstance(u,Unit):
                    strResult += u.toSqlite()

        return strResult


    def toSVGGanttMarker(self,dateBase):

        """  """

        strResult = ''

        if self.child:
            strResult += '<g>'
            for v in self.child:
                for u in v:
                    if u.isMarked():
                        x_i = (u.dt.date() - dateBase).days * 2
                        strResult += '<line stroke="red" stroke-width="1" x1="{}" y1="{}" x2="{}" y2="{}">\n'.format(x_i, 0, x_i, config.diagram_width)
                        strResult += f'<title>{u}</title>\n'
                        strResult += '</line>'
            strResult += '</g>'

        return strResult


    def toSVG(self, x = config.diagram_offset, y=0):

        """  """

        strResult = '<g>'

        if self.color is not None:
            strResult += '<rect fill="{}" opacity=".5" x="{}" y="{}" height="{}" width="{}"/>\n'.format(self.color,1,y+1,((config.diagram_bar_height * 2)*len(self.child))-2,x+config.diagram_width-4)

        strResult += '<text x="{}" y="{}" style="vertical-align:top" text-anchor="right"><tspan x="10" dy="1.5em">{}</tspan><tspan x="10" dy="1.5em">{}</tspan><title>{}</title></text>\n'.format(0,y,self.getTitleXML(), self.getDateString(), (self.getTitleXML() + self.getDateString() + '\n\n' + self.getDescriptionString() + '\n\n' + self.report()))

        if not self.child:
            pass
        else:
            y += config.diagram_bar_height / 2
            t = date.today()
            d = self.dateBegin
            for v in self.child:
                strResult += '<line stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(x,y,x,y+config.diagram_bar_height)

                if d.month == t.month and d.day == t.day:
                    strResult += '<rect fill="{}" x="{}" y="{}" height="{}" width="{}"/>\n'.format('#ffaaaa',x,y-1,config.diagram_bar_height+2,config.diagram_width - config.diagram_offset)
                    #if d.year == t.year:
                    #    strResult +=  '<foreignObject x="{}" y="{}" height="{}" width="{}"><a xmlns="http://www.w3.org/1999/xhtml" name="today"/></foreignObject>\n'.format(x,y-1,config.diagram_bar_height+2,config.diagram_width - config.diagram_offset)
                elif d.isoweekday() == 6 or d.isoweekday() == 7:
                    strResult += '<rect fill="{}" x="{}" y="{}" height="{}" width="{}"/>\n'.format('#eeeeee',x,y-1,config.diagram_bar_height+2,config.diagram_width - config.diagram_offset)
                d += timedelta(days=1)

                n = ''
                x_i = x
                for u in v:
                    if isinstance(u,Note):
                        # collect all notes of day v
                        n += u.getDescriptionString() + ' '
                    else:
                        strResult += u.toSVG(x_i,y)
                        if isinstance(u,Unit) or isinstance(u,Combination):
                            x_i += u.getDuration().total_seconds() / 3600 * 25 * config.diagram_scale_dist + 5
                    # TODO: add unit marker if u.isMarked()
                if n:
                    strResult += '<text x="{}" y="{}" style="">{}</text>\n'.format(x_i + 2,y + config.diagram_bar_height,n)

                y += config.diagram_bar_height * 2

        strResult += '</g>'

        return strResult


    def toSVGDiagram(self):

        """  """

        diagram_height = len(self.child) * (config.diagram_bar_height * 2) + 0

        strResult = '<svg baseProfile="full" height="{}" version="1.1" width="{}" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink">'.format(diagram_height, config.diagram_width)

        strResult += '<style type="text/css">svg { font-family: ' + config.font_family + '; font-size: ' + str(config.font_size) + 'pt; }</style>'
        strResult += '<g>'

        strResult += '<rect fill="transparent" stroke="{}" stroke-width="2" x="{}" y="{}" rx="3" ry="3" height="{}" width="{}"/>\n'.format('#aaaaaa', 0, 0, diagram_height, config.diagram_width)

        for i in [3600/4,3600/2,3600,2*3600,3*3600,4*3600,5*3600,6*3600]:
            w = config.diagram_offset + i / 3600 * 25 * config.diagram_scale_dist
            strResult += '<line stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(w, 0, w, diagram_height)

        strResult += self.toSVG()

        strResult += '</g>'
        strResult += '</svg>\n'

        return strResult


    def toSVGGanttChart(self):

        """ Gantt chart of this cycle """

        d_0 = self.dateBegin
        d_1 = self.dateEnd

        diagram_height = 40 * (config.diagram_bar_height * 2) + 100
        try:
            diagram_width = ((d_1 - d_0).days) * 2 + 100
        except ValueError:
            return ''

        strResult = '<svg baseProfile="full" height="{}" version="1.1" width="{}" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink">'.format(diagram_height, diagram_width)

        strResult += '<style type="text/css">svg { font-family: ' + config.font_family + '; font-size: ' + str(config.font_size) + 'pt; }</style>'

        strResult += '<g transform="translate(10,10)">'

        strResult += '<g>'

        m = round((d_1 - d_0).total_seconds() / (30 * 24 * 60 * 60))
        for i in range(0,m+1):
            d_i = date(d_0.year+round(i//12),i%12+1,1)
            w = ((d_i - d_0).days + 1) * 2
            if i % 12:
                color = 'black'
            else:
                color = 'red'

            strResult += '<line stroke-dasharray="8" stroke="{}" stroke-width="1" opacity="0.5" x1="{}" y1="{}" x2="{}" y2="{}">\n'.format(color,w, 0, w, diagram_height)
            strResult += '<title>{}</title>\n'.format(d_i.strftime("%Y-%m-%d"))
            strResult += '</line>'
            strResult += '<g transform="translate({},{})">'.format(w+8, diagram_height - 105)
            strResult += '<g transform="rotate(-45)">'
            strResult += '<text x="{}" y="{}">{}</text>\n'.format(0, 0, d_i.strftime("%Y-%m-%d"))
            strResult += '</g>'
            strResult += '</g>'

        w = ((date.today() - d_0).days + 1) * 2
        strResult += '<line stroke="red" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(w, 0, w, diagram_height)
        strResult += '</g>'

        for i in [0,30,45,60,90]:
            strResult += '<line stroke-dasharray="2" stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(0, diagram_height - 10 - i, diagram_width, diagram_height - 10 - i)

        strResult += self.toSVGGanttBar(d_0)
        
        # TODO: add unit marker if u.isMarked()

        strResult += '</g>'
        strResult += '</svg>\n'

        return strResult


    def toSVGGanttBar(self,dateBase,y=0):

        """ returns SVG string of vertical and horizontal bars in Gantt Chart """

        l = self.getPeriodDone()

        # TODO: make config.diagram_height configurable
        config.diagram_height = 40 * (config.diagram_bar_height * 2) + 100

        x_i = (self.dateBegin - dateBase).days * 2

        strResult = '<g>'

        # horizontal bar

        if self.color is not None:
            color = self.color
        else:
            color = '#ffaaaa'

        strResult += '<a href="#{}">'.format(str(id(self)))
        strResult += '<rect opacity=".75" stroke="red" stroke-width=".5" fill="{}" x="{}" y="{}" height="{}" width="{}" rx="2">\n'.format(color, x_i, y, config.diagram_bar_height*2, len(self) * 2)
        strResult += '<title>{}</title>\n'.format(self.getTitleXML() + self.getDateString() + ' ' + self.getDescriptionString())
        strResult += '</rect>'
        strResult += '</a>'

        # vertical bar

        h = round(self.getDuration().total_seconds() / 60 / l)

        if self.color is not None:
            scolor = 'red'
            color = self.color
        elif h > 20:
            scolor = 'green'
            color = '#aaffaa'
        elif h > 4:
            scolor = 'red'
            color = '#ffaaaa'
        else:
            h = 2
            scolor = 'red'
            color = 'red'

        strResult += '<a href="#{}">'.format(str(id(self)))
        strResult += '<rect opacity=".75" stroke="{}" stroke-width=".5" fill="{}" x="{}" y="{}" height="{}" width="{}">\n'.format(scolor, color, x_i + 1, config.diagram_height - h - 10, h, l * 2 - 2)
        strResult += '<title>{}</title>\n'.format(self.getTitleXML() + self.getDateString() + '\n\n' + self.getDescriptionString() + '\n\n' + self.report())
        strResult += '</rect>'
        strResult += '</a>'

        #strResult += '<text x="{}" y="{}">{}</text>\n'.format(x_i,y,self.getTitleXML())
        strResult += '</g>'

        return strResult

    
    def toFreemindNode(self):

        """  """

        strResult = '<node' + self.toFreemindNodeAttr() + '>\n'
        #strResult += '<font BOLD="false" NAME="Monospaced" SIZE="12"/>'

        strResult += self.getDescriptionFreemind()

        d_i = self.dateBegin
        for v in self.child:
            strResult += '<node TEXT="' + d_i.strftime("%Y-%m-%d %a") + '"'
            if d_i.isoweekday() == 6 or d_i.isoweekday() == 7:
                strResult += ' BACKGROUND_COLOR="#eeeeee"'
            strResult += '>'
            for u in v:
                strResult += u.toFreemindNode()
            strResult += '</node>\n'
            d_i += timedelta(days=1)

        strResult += '</node>\n'

        return strResult


    def to_ical(self,cal):

        """  """

        event = Event()
        event.add('summary', 'Cycle: {}'.format(self.title))
        event.add('dtstart', self.dateBegin)
        event.add('dtend', self.dateEnd + timedelta(days=1))
        event.add('dtstamp', datetime.now().astimezone(None))
        cal.add_component(event)

        for v in self.child:
            for u in v:
                u.to_ical(cal)


    def toVCalendar(self):

        """  """

        cal = Calendar()
        cal.add('prodid', '-//{title}//  //'.format(title=self.title))
        cal.add('version', '2.0')
        self.to_ical(cal)
        return cal.to_ical()


if __name__ == '__main__':

    print('Module Test: ' + __file__ + '\n')

    t = Cycle('C1')
    t.insert([1,3],Unit(';;RB;0:30:00'))
    t.append(Unit(';30;BB;01:00:00'))
    t.appendDescription('Running Blocks')
    t.extend(8)
    
    u = Cycle('C2')
    u.insert([0,2,4,6],Unit(';;RI;0:30:00'))
    t.append(u)

    #v = Cycle('C3')
    #u.insert([1,5],Unit(';;RY;0:30:00'))
    #t.overwrite(u)

    t.schedule(2025,3,4)
    print(t)
