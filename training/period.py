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

import io

import os

from pathlib import Path

import sys

import math

import copy

import re

from statistics import mean

from datetime import timedelta, date, datetime, time, timezone

from suntime import Sun

from icalendar import Calendar, Event, Alarm

import numpy as np

from training import config as config
from training.titem import TItem
from training.tcontainer import TContainer

from training.note import Note
from training.unit import Unit
from training.combination import Combination
from training.exerciseset import ExerciseSet
#from training.plot import Plot
from training.phase import Phase
from training.cycle import Cycle
from training.bunch import Bunch

#
#
#

class Period(TContainer):

    def __init__(self,t=None,l=0):

        """  """

        super().__init__(t,l)


    def __str__(self):

        strResult = super().__str__()

        for c in self.child:
            strResult += f'{c}\n'

        return strResult + '\n\n'


    def updateValues(self,dictArg=None):

        """  """

        for c in self.child:
            if isinstance(c,TContainer):
                c.updateValues(dictArg)

        return self


    def resetDistances(self):

        """  """

        self.clean()

        for c in self.child:
            if isinstance(c,TContainer):
                c.resetDistances()

        return self


    def getLength(self):

        """ return length of period """

        l = 0
        for c in self.child:
            if isinstance(c,TContainer):
                l += c.getLength()

        if (self.periodInt is None or self.periodInt < 1) and l > 0:
            self.setPeriod(l)

        return self.periodInt


    def getItem(self,index):

        """ return item of index in period """

        if type(index) is int:
            return self.child[index]
        elif type(index) is list:
            if len(index) == 1:
                return self.child[index[0]]
            elif len(index) > 1:
                return self.child[index[0]].getItem(index[1:])
    
        return None


    def getDuration(self, skipType=None):

        """ return a timedelta """

        # TODO: use self.data

        if skipType is None:
            skipType = self.skipType

        intResult = 0

        for u in self.child:
            if isinstance(u,TContainer):
                intResult += u.getDuration(skipType).total_seconds()

        return timedelta(seconds=intResult)


    def getNumberOfCycles(self):

        """  """

        intResult = 0

        for c in self.child:
            if isinstance(c,Cycle) or isinstance(c,Bunch):
                intResult += c.getNumberOfCycles()

        return intResult


    def getMarkers(self, dt0=None, dt1=None):

        """  """

        listResult = []

        for c in self.child:
            if isinstance(c,Cycle) or isinstance(c,Period):
                listResult.extend(c.getMarkers(dt0,dt1))

        return listResult


    def getNumberOfUnits(self, dt0=None, dt1=None):

        """  """

        # TODO: use self.data

        intResult = 0

        for c in self.child:
            if isinstance(c,TContainer):
                intResult += c.getNumberOfUnits(dt0,dt1)

        return intResult


    def append(self,o):

        """ append o to the list of childs """

        self.clean()

        if o is None:
            print('error: ' + str(o), file=sys.stderr)
        elif isinstance(o,list):
            for a in o:
                self.append(a)
        elif isinstance(o,TContainer) or isinstance(o,Note):
            self.child.append(o.dup())
            self.periodInt += o.getLength()
            #self.schedule()
        else:
            print('error: ' + str(o), file=sys.stderr)

        return self


    def extend(self,n=7):

        """ append last n days at the end """

        if type(n) is int and n > 0 and self.periodInt >= n:
            self.scale((self.periodInt + n) / self.periodInt)
            self.setPeriod(self.periodInt + n)

        return self


    def ins(self,o,**kwargs):
        
        """ 
        
        insert(item=TItem,Replace=True) 
        
        insert(date=date(),level=l,item=TItem) 
        
        insert(path=[1,0,4,3],item=TItem) 
        
        insert(level=1,container=TContainer) 
        
        insert(path=[1,0,4,3],container=TContainer,Replace=False) 
        
        replace(path=[1,0,4,3],container=TContainer) = insert(path=[1,0,4,3],container=TContainer,Replace=True)

        """

        objResult = self

        if type(o) is list:
            if 'date' in kwargs:
                for a in o:
                    objResult = self.ins(a,**kwargs)
                    kwargs['date'] += timedelta(days=a.periodInt)
                self.dateEnd = kwargs['date']
            else:
                for a in o:
                    objResult = self.ins(a,**kwargs)
                
        elif isinstance(o,TItem):
            l = list(self.qy(date=o.dt))
            if l is None or len(l) < 1:
                print('error: no according Container found' + str(o), file=sys.stderr)
            else:
                c = l[-1]
                c.insert((o.dt.date() - c.dateBegin).days, o)

        elif isinstance(o,TContainer):            
            l = list(self.qy(date=o.dateBegin,type=Period,**kwargs))
            if l is None or len(l) < 1:
                #print('error: no according Container found' + str(o), file=sys.stderr)
                self.child.append(o.dup())
                #self.schedule()
            else:
                p = l[-1]
                n = o.dup()
                n.dateFixed = o.dateBegin
                if len(p.child) < 1:
                    p.child.append(n)
                    #p.dateBegin, p.dateEnd = n.dateBegin, n.dateEnd
                else:
                    for i in range(len(p.child)):
                        if isinstance(p.child[i],TContainer):
                            if p.child[i].isDateInContainer(n.dateBegin):
                                if p.child[i].dateBegin == n.dateBegin:
                                    # begin is equal
                                    p.child.insert(i,n)
                                    break
                                elif p.child[i].dateEnd >= n.dateBegin:
                                    # n begins in p.child[i]
                                    p.child[i].cutAfter(n.dateBegin - timedelta(days=1))
                                    p.child.insert(i+1,n)
                                    break
                            elif p.child[i] == p.child[-1]:
                                print('error: no cycle found', file=sys.stderr)
                                p.child.append(n)
                    #self.schedule()

            return self.schedule()
        
            if 'path' in kwargs:
                # insert via path
                objResult = self.ins(o,path=kwargs['path'][1:-1])
                
            elif self.dateBegin is None:
                print('error: date begin', file=sys.stderr)
                
            elif 'date' not in kwargs:
                if o.dateBegin is None:
                    print('error: date begin', file=sys.stderr)
                else:
                    objResult = self.ins(o,date=o.dateBegin)
                                    
            elif 'level' not in kwargs or kwargs['level'] < 1:
                # insert via date and default level
                objResult = self.ins(o,date=kwargs['date'],level=1)
            
            else:
                # insert via date and level
                p = self.getContainerByDate(kwargs['date'],kwargs['level'])
                if p is None:
                    print('error: no according period found' + str(o), file=sys.stderr)
                else:
                    n = o.dup().schedule(kwargs['date'])
                    if len(p.child) < 1:
                        p.child.append(n)
                        #p.dateBegin, p.dateEnd = n.dateBegin, n.dateEnd
                    else:
                        for i in range(len(p.child)):
                            if isinstance(p.child[i],TContainer):
                                if p.child[i].isDateInContainer(n.dateBegin):
                                    if p.child[i].dateBegin == n.dateBegin:
                                        # begin is equal
                                        p.child.insert(i,n)
                                        break
                                    elif p.child[i].dateEnd >= n.dateBegin:
                                        # n begins in p.child[i]
                                        p.child[i].cutAfter(n.dateBegin - timedelta(days=1))
                                        p.child.insert(i+1,n)
                                        break
                                elif p.child[i] == p.child[-1]:
                                    print('error: no cycle found', file=sys.stderr)
                                    p.child.append(n)
                #self.schedule()
                
        else:
            print('error: type', file=sys.stderr)
 
        return objResult


    def insert(self,o,intLevel=-1):

        """  """

        objResult = self

        if o is None:
            print('error: object', file=sys.stderr)
        elif self.dateBegin is None:
            print('error: date begin', file=sys.stderr)
        elif isinstance(o,TContainer):
            if o.dateBegin is None:
                print('error: date begin', file=sys.stderr)
            else:
                p = self.getPeriodByDate(o.dateBegin,intLevel)
                if p is None:
                    print('error: no according period found' + str(o), file=sys.stderr)
                elif not p.child:
                    p.child.append(o.dup())
                else:
                    for i in range(len(p.child)):
                        if isinstance(p.child[i],TContainer):
                            if p.child[i].dateBegin == o.dateBegin:
                                # begin is equal
                                p.child.insert(i,o.dup())
                                break
                            elif p.child[i].dateEnd >= o.dateBegin:
                                # o begins in p.child[i]
                                p.child[i].cutAfter(o.dateBegin - timedelta(days=1))
                                p.child.insert(i+1,o.dup())
                                break
                            elif p.child[i] == p.child[-1]:
                                print('error: no cycle found', file=sys.stderr)
                                p.child.append(o.dup())
                self.schedule()
        elif isinstance(o,TItem):
            if o.dt is None:
                print('error: date', file=sys.stderr)
            else:
                c = self.getContainerByDate(o.dt)
                if c is None or not c.child:
                    print('error: no cycle found', file=sys.stderr)
                else:
                    # is inside this Cycle
                    j = round((o.dt.date() - c.dateBegin).total_seconds() / (24 * 60 * 60))
                    c.insert(j,o.dup())
                self.schedule()

        return objResult


    def insertByDate(self,o,f=False,intLevel=10):

        """ returns a reference to an object which was inserted according its date(s) """

        objResult = None

        if isinstance(o,TContainer):
            for c in self.qy(date=o.dateBegin,level=intLevel,type=Period):
                c.insert(o)
                break
        else:
            for c in self.qy(date=o.dt,type=Cycle):
                c.insert((o.dt.date() - c.dateBegin).days, o)
                break

        return objResult


    def scale(self,f,p=None):

        """ returns a copy of self, scaled by f and matching pattern p if not None """

        r = self.dup()
        if f > 0.01 and abs(f - 1.0) > 0.01:
            for i in range(len(r.child)):
                if isinstance(r.child[i],TContainer):
                    r.child[i] = r.child[i].scale(f,p)

        r.summary.clear()

        return r


    def overwrite(self,c,d=None):

        """ overwrite the descendant cycle sequence by c """

        if isinstance(c,Cycle):
            if d:
                c = self.getContainerByDate(d)
                if isinstance(c,Cycle):
                    c.insert((d - c.dateBegin).days,c,True)
            elif c.dateBegin:
                self.overwrite(c,c.dateBegin)
            else:
                self.overwrite(c, self.dateBegin)
        else:
            print(f'error: inserting {type(c)} at date {d}', file=sys.stderr)

        return self


    def removeChilds(self,l):

        """  """

        l.sort(reverse=True)
        for i in l:
            if isinstance(self.child[i],TContainer):
                del self.child[i]

        self.data = []

        return self


    def removeCycles(self):

        """  """

        for i in range(len(self.child)-1,-1,-1):
            if isinstance(self.child[i],Period):
                self.child[i].removeCycles()
            elif isinstance(self.child[i],Cycle):
                del self.child[i]

        self.data = []

        return self


    def remove(self,p=None):

        """  """

        for c in self.child:
            if isinstance(c,TContainer):
                c.remove(p=p)

        self.clean()

        return self


    def cutBefore(self,d):

        """  """

        assert type(d) is date

        if self.dateBegin < d and d <= self.dateEnd:
            for i in range(len(self.child)):
                if isinstance(self.child[i],TContainer):
                    if d == self.child[i].dateBegin:
                        del self.child[:i]
                        break
                    elif self.child[i].dateBegin < d and d <= self.child[i].dateEnd:
                        self.child[i].cutBefore(d)
                        del self.child[:i]
                        break

            #for i in range(len(self.tag)):
            #    if d <= self.tag[i].dateBegin or self.tag[i].dateEnd <= d:
            #        del self.tag[i]
            #        i -= 1

            self.setPeriod((self.dateEnd - d).days + 1)
            self.schedule(d)
            self.clean()

        return self


    def cutAfter(self,d):

        """  """

        assert type(d) is date

        if self.dateBegin <= d and d < self.dateEnd:
            for i in range(len(self.child)):
                if isinstance(self.child[i],TContainer):
                    if d == self.child[i].dateEnd:
                        del self.child[i+1:]
                        break
                    elif self.child[i].dateBegin <= d and d < self.child[i].dateEnd:
                        self.child[i].cutAfter(d)
                        del self.child[i+1:]
                        break

            self.setPeriod((d - self.dateBegin).days + 1)
            self.schedule(self.dateBegin)
            self.clean()

        return self


    def addTags(self, o=None):

        """  """

        if type(o) is list:
            self.tag.extend(o)
        elif isinstance(o,Phase):
            self.tag.append(o)

        return self


    def stat(self, dt0=None, dt1=None, skipType=None):

        """ stat all descendant data to self.data and returns it as a nested list  """

        self.clean()

        if skipType is None:
            skipType = self.skipType
        for c in self.child:
            if isinstance(c,TContainer):
                self.data.extend(c.stat(dt0,dt1,skipType))

        return self.data


    def toHtmlTable(self):

        """  """

        strResult = f'<section {config.getClass(__name__)} id="{str(id(self))}"'

        if self.color is not None:
            strResult += ' style="background-color: {}"'.format(self.color)

        strResult += '><div class="header" ondblclick="removeDetails(this);" title="Double Click to hide the details">' + self.getTitleXML()
        if self.dateBegin is not None and self.dateEnd is not None:
            strResult += self.getDateString()
        strResult += '</div>\n'

        strResult += self.getDescriptionHTML()

        if self.getNumberOfUnits() > 0 or self.data:
            strResult += f'<pre {config.getClass(__name__)}>' + self.report() + '</pre>'

        m = self.getMarkers()
        if len(m) > 0:
            strResult += '<p>Marked Units (Peaks)</p>'
            strResult += '<ol>'
            for c in m:
                strResult += f'<li>{c}</li>'
            strResult += '</ol>'

        if self.fPlot:
            strResult += '<div style="text-align: center;margin: 0px;">'
            #strResult += self.plotAccumulationDuration()
            #strResult += self.plotAccumulation()
            #strResult += self.plotHist()
            #strResult += self.plotTimeDist()
            strResult += self.toSVGGanttChart()
            #strResult += self.toSVGDiagram()
            strResult += '</div>'

        for c in self.child:
            strResult += c.toHtmlTable() + '\n'

        strResult += '</section>\n'

        return strResult


    # define simple Alias
    toHtml = toHtmlTable


    def toCSV(self):

        """  """

        strResult = ""
        if self.dateBegin is not None:
            strResult += self.dateBegin.strftime("%Y-%m-%d")
        strResult += ';;;;Period "{}" {}\n\n'.format(self.title, self.getDateString())

        for c in self.child:
            strResult += c.toCSV()
        strResult += '\n'

        return strResult


    def toFreemindNode(self):

        """  """

        strResult = '<node' + self.toFreemindNodeAttr() + '>\n'
        #strResult += '<font BOLD="true" NAME="Monospaced" SIZE="12"/>'
        strResult += self.getDescriptionFreemind()

        for c in self.child:
            strResult += c.toFreemindNode()

        strResult += '</node>\n'

        return strResult


    def toSqlite(self):

        """  """

        strResult = ''
        for c in self.child:
            if isinstance(c,Cycle) or isinstance(c,Period):
                strResult += c.toSqlite()

        return strResult


    def toSVG(self, x = config.diagram_offset, y=20):

        """ returns SVG code for Period 'self' in a vertical Timeline """

        l = self.getLength()
        strResult = '<g>'

        if self.color is not None and l > 0:
            strResult += '<rect fill="{}" opacity=".5" x="{}" y="{}" height="{}" width="{}"/>\n'.format(self.color,1,y+1,((config.diagram_bar_height * 2) * l)-2,x+config.diagram_width-4)

        if not self.child:
            strResult += '<text x="{}" y="{}" style="vertical-align:top"><tspan x="10" dy="1.5em">{}</tspan><tspan x="10" dy="1.5em">{}</tspan></text>\n'.format(0,y,self.getTitleXML(), self.getDateString())
            strResult += '<line stroke="black" stroke-width=".5" stroke-dasharray="2,10" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(0,y,x+config.diagram_width,y)
            for d in range(0,l):
                strResult += '<line stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(x,y,x,y+config.diagram_bar_height)
                y += config.diagram_bar_height * 2
        else:
            for c in self.child:
                if isinstance(c,TContainer):
                    strResult += '<line stroke="black" stroke-width=".5" stroke-dasharray="2,10" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(0,y,config.diagram_width,y)
                    strResult += c.toSVG(x,y)
                    y += len(c) * config.diagram_bar_height * 2

        strResult += '</g>'

        return strResult


    def toSVGGantt(self,dateBase,y=0):

        """ Gantt chart of this Bunch (horizontal timeline) """

        try:
            l = self.dateEnd - self.dateBegin
            x_i = (self.dateBegin - dateBase).days * 2
        except TypeError:
            return '<text x="{}" y="{}">{}</text>\n'.format(0 + 2, y + 10,self.getTitleXML())

        strResult = '<g>'

        if self.color is not None:
            c = self.color
        elif not self.child:
            # high level definition period
            c = '#aaffaa'
        else:
            c = "#c7c7fc"

        strResult += '<a href="#{}">\n'.format(str(id(self)))
        strResult += '<rect fill="{}" stroke="black" stroke-width=".5" x="{}" y="{}" height="{}" width="{}" rx="2">\n'.format(c, x_i, y, config.diagram_bar_height*2, (l.days + 1) * 2)
        strResult += '<title>{}</title>\n'.format(self.getTitleXML() + self.getDateString() + '\n\n' + self.getDescriptionSVG() + '\n\n' + self.report())
        strResult += '</rect>'
        if self.getLength() > 13:
            strResult += '<text x="{}" y="{}">{}</text>\n'.format(x_i + 2, y + 12,self.getTitleXML())
        strResult += '</a>\n'

        y_i = y + config.diagram_bar_height * 3
        for c in self.child:
            if isinstance(c,TContainer):
                if isinstance(c,Cycle):
                    strResult += c.toSVGGanttMarker(dateBase)
                strResult += c.toSVGGanttBar(dateBase,y_i)
                if isinstance(c,Period):
                    strResult += c.toSVGGantt(dateBase,y_i)
                y_i += config.diagram_bar_height * 3
                
        strResult += '<line stroke-dasharray="4" stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(x_i + (l.days + 1) * 2, y, x_i + (l.days + 1) * 2, y_i)

        strResult += '</g>'

        return strResult


    def toSVGGanttSheet(self,d_0, d_1, diagram_height, diagram_width):

        """ Calendar """

        strResult = '<g id="months">'
        # marker date
        d_i = date(d_0.year, d_0.month, 1)
        m = round((d_1 - d_0).total_seconds() / (30 * 24 * 60 * 60)) + 1
        for i in range(m):
            if d_i.month == 1:
                color = 'red'
            else:
                color = 'black'

            # line marker
            w = ((d_i - d_0).days + 1) * 2
            strResult += '<line stroke-dasharray="8" stroke="{}" stroke-width="1" opacity="0.25" x1="{}" y1="{}" x2="{}" y2="{}">\n'.format(color,w, 0, w, diagram_height)
            strResult += '<title>{}</title>\n'.format(d_i.strftime("%Y-%m-%d"))
            strResult += '</line>'

            strResult += '<g transform="translate({},{})">'.format(w+8, diagram_height - 105)
            strResult += '<g transform="rotate(-45)">'
            strResult += '<text x="{}" y="{}">{}</text>\n'.format(0, 0, d_i.strftime("%Y-%m-%d"))
            strResult += '</g>'
            strResult += '</g>'

            if d_i.month > 11:
                d_i = date(d_i.year + 1, 1, 1)
            else:
                d_i = date(d_i.year, d_i.month + 1, 1)

        w = ((date.today() - d_0).days) * 2
        strResult += '<rect fill="red" opacity=".5" stroke="red" stroke-width=".5" x="{}" y="{}" width="{}" height="{}">\n'.format(w, 0, 2, diagram_height)
        strResult += '<title>Today {}</title>\n'.format(date.today().strftime("%Y-%m-%d"))
        strResult += '</rect>'
        strResult += '</g>'

        strResult += '<g id="tags">'
        for t in self.tag:
            if isinstance(t,Phase):
                if (t.date + timedelta(days=t.duration) < d_0) or (t.date >= d_1):
                    # out of interval
                    continue
                elif d_0 < t.date and d_1 < t.date + timedelta(days=t.duration):
                    # only start is inside interval
                    x_i = (t.date - d_0).days
                    w_i = (d_1 - t.date).days + 1
                elif t.date < d_0 and t.date + timedelta(days=t.duration) < d_1:
                    # only end is inside interval
                    x_i = 0
                    w_i = (t.date + timedelta(days=t.duration) - d_0).days + 1
                else:
                    # is in interval
                    x_i = (t.date - d_0).days
                    w_i = t.duration

                strResult += '<a href="#{}">\n'.format(str(id(t)))
                strResult += '<rect fill="{}" opacity=".5" stroke="none" stroke-width=".5" x="{}" y="{}" height="{}" width="{}" rx="2">\n'.format(t.color, x_i * 2, 0, diagram_height - 10, w_i * 2)
                strResult += f'<title>{t.title} ({t.duration} {t.date.strftime("%Y-%m-%d")} {(t.date + timedelta(days=t.duration - 1)).strftime("%Y-%m-%d")})</title>\n'
                strResult += '</rect>'
                strResult += '</a>'
        strResult += '</g>'

        strResult += '<g id="minutes">'
        for i in [0,30,45,60,90]:
            strResult += '<line stroke-dasharray="2" stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(0, diagram_height - 10 - i, diagram_width, diagram_height - 10 - i)
        strResult += '</g>'

        return strResult


    def toSVGGanttChart(self):

        """ Gantt chart of periods and cycles """

        if self.child:
            # detailed definition of period (Cycle and Period childs)
            d_0 = None
            d_1 = None
            for c in self.child:
                if isinstance(c,TContainer):
                    if d_0 is None:
                        d_0 = c.dateBegin
                    if d_1 is None:
                        d_1 = self.child[-1].dateEnd

            if self.dateBegin is None:
                self.dateBegin = d_0

            if self.dateEnd is None:
                self.dateEnd = d_1
        else:
            # high level definition of period (stat only)
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

        strResult += '<g id="sheet">'
        strResult += self.toSVGGanttSheet(d_0,d_1,diagram_height,diagram_width)
        strResult += '</g>'
        
        strResult += '<g id="periods">'
        strResult += self.toSVGGantt(d_0)
        strResult += '</g>'

        strResult += '</g>'
        strResult += '</svg>\n'

        return strResult


    def toSVGGanttBar(self,dateBase,y=0):

        """ returns SVG string of vertical and horizontal bars in Gantt Chart """

        l = (self.dateEnd - self.dateBegin).days + 1

        # TODO: make config.diagram_height configurable
        config.diagram_height = 40 * (config.diagram_bar_height * 2) + 100

        x_i = (self.dateBegin - dateBase).days * 2

        strResult = '<g>'

        if self.color is not None:
            color = self.color
        else:
            color = '#ffaaaa'

        strResult += '<a href="#{}">'.format(str(id(self)))
        strResult += '<rect opacity=".75" stroke="red" stroke-width=".5" fill="{}" x="{}" y="{}" height="{}" width="{}" rx="2">\n'.format(color, x_i, y, config.diagram_bar_height*2, len(self) * 2)
        strResult += '<title>{}</title>\n'.format(self.getTitleXML() + self.getDateString() + ' ' + self.getDescriptionString())
        strResult += '</rect>'
        strResult += '</a>'

        strResult += '</g>'

        return strResult


    def to_ical(self,cal):

        """  """

        if not self.child:
            event = Event()
            event.add('summary', 'Period: {}'.format(self.title))
            event.add('dtstart', self.dateBegin)
            event.add('dtend', self.dateEnd + timedelta(days=1))
            event.add('dtstamp', datetime.now().astimezone(None))
            cal.add_component(event)

        else:
            fOutput = False
            for c in self.child:
                c.to_ical(cal)
                if isinstance(c,Cycle):
                    # output only, if there is a Cycle child involved
                    fOutput = True

            if fOutput and self.dateBegin is not None and hasattr(self,'title'):
                event = Event()
                event.add('summary', 'Begin Period: ' + self.title)
                event.add('dtstart', self.dateBegin)
                event.add('dtend', self.dateBegin + timedelta(days=1))
                event.add('dtstamp', datetime.now().astimezone(None))
                cal.add_component(event)

            if fOutput and self.dateEnd is not None and hasattr(self,'title'):
                event = Event()
                event.add('summary', 'End Period: ' + self.title)
                event.add('dtstart', self.dateEnd)
                event.add('dtend', self.dateEnd + timedelta(days=1))
                event.add('dtstamp', datetime.now().astimezone(None))
                cal.add_component(event)


    def toVCalendar(self):

        """  """

        cal = Calendar()
        cal.add('prodid', '-//{title}//  //'.format(title=self.title))
        cal.add('version', '2.0')
        self.to_ical(cal)
        return cal.to_ical()


    #
    #
    #

    @staticmethod
    def CalendarYearPeriod(intYear,strArg=None):

        """ returns a plain calendar year period """

        r = Period(strArg)
        
        try:
            date(intYear, 2, 29)
            r.append(Cycle(str(intYear),366))
        except ValueError:
            r.append(Cycle(str(intYear),365))

        if strArg is not None and strArg:
            r.set(title=strArg)

        r.schedule(intYear,1,1)

        return r


    @staticmethod
    def CalendarSeasonPeriod(intYear,strArg=None):

        """ returns a plain calendar year containing seasons periods """

        r = Period(strArg)

        # begin of year
        d_0 = date(intYear,1,1)

        s = 'Winter {}'.format(intYear)
        # begin of spring
        d_1 = date(intYear,3,21)
        r.append(Period(s).append(Cycle(s, round((d_1 - d_0).total_seconds() / (24 * 60 * 60)))))

        s = 'Spring {}'.format(intYear)
        # begin of summer
        d_2 = date(intYear,6,21)
        r.append(Period(s).append(Cycle(s, round((d_2 - d_1).total_seconds() / (24 * 60 * 60)))))

        # begin of autumn
        s = 'Summer {}'.format(intYear)
        d_3 = date(intYear,9,21)
        r.append(Period(s).append(Cycle(s, round((d_3 - d_2).total_seconds() / (24 * 60 * 60)))))

        s = 'Autumn {}'.format(intYear)
        # begin of winter
        d_4 = date(intYear,12,21)
        r.append(Period(s).append(Cycle(s, round((d_4 - d_3).total_seconds() / (24 * 60 * 60)))))

        s = 'Winter ' + str(intYear+1)
        # begin of next year
        d_5 = date(intYear+1,1,1)
        r.append(Period(s).append(Cycle(s, round((d_5 - d_4).total_seconds() / (24 * 60 * 60)))))

        if strArg is not None and strArg:
            r.set(title=strArg)

        r.schedule(intYear,1,1)

        return r


    @staticmethod
    def CalendarWeekPeriod(intYear,strArg=None):

        """ fills a period calendar year containing week periods """

        r = Period(strArg)

        for w in range(1,54):
            r.append(Cycle('CW{}/{}'.format(w, intYear), 7))

        d = date(intYear,1,1)
        if d.isoweekday() > 4:
            # skip to next monday
            d += timedelta(days=(8 - d.isoweekday()))
        else:
            # skip to previous monday
            d -= timedelta(days=(d.isoweekday() - 1))

        if strArg is not None and strArg:
            r.set(title=strArg)

        r.schedule(d)

        return r


    @staticmethod
    def CalendarMonthPeriod(intYear,strArg=None):

        """ returns a calendar year containing month periods """

        r = Period(strArg)

        for m in range(1,13):
            if m > 11:
                d = date(intYear+1,1,1) - date(intYear,m,1)
            else:
                d = date(intYear,m+1,1) - date(intYear,m,1)

            r.append(Cycle('{}.{}'.format(intYear,m), d.days))

        if strArg is not None and strArg:
            r.set(title=strArg)

        r.schedule(intYear)

        return r


    @staticmethod
    def CalendarLastWeeksPeriod(intWeek=26,strArg=None):

        """ returns a last weeks as periods """

        r = Period(strArg)

        dt_0 = datetime.now().date()
        dt_i = dt_0 + timedelta(days=(7 - dt_0.weekday())) - timedelta(weeks=intWeek)
        r.dateFixed = dt_i

        for m in range(0,intWeek):
            r.append(Cycle(dt_i.strftime("%Y-W%U")))
            dt_i += timedelta(weeks=1)

        if strArg is not None and strArg:
            r.set(title=strArg)

        r.schedule()

        return r


    @staticmethod
    def CalendarLastMonthsPeriod(intMonth=6,strArg=None):

        """ returns a last months (= 4 weeks) as periods """

        r = Period(strArg)

        dt_0 = datetime.now().date()
        dt_i = dt_0 + timedelta(days=(7 - dt_0.weekday())) - timedelta(weeks = intMonth * 4)
        r.dateFixed = dt_i

        for m in range(0,intMonth):
            r.append(Cycle(dt_i.strftime("%Y-M%m"),4*7))
            dt_i += timedelta(weeks=4)

        if strArg is not None and strArg:
            r.set(title=strArg)

        r.schedule()

        return r



if __name__ == '__main__':

    t = Period('General Basics').appendDescription('Global Plan')
    u = Period('General Basics A')
    w = Period('Week General Basics A',7)
    u.append([w,w,w])
    t.append([u,u])
    t.schedule(2025,3,4)
    t.cutAfter(date(2025,4,3))
    t.scale(2.0) # must not raise an error
    print(t)
    #print(t.toHtml())
    #print(t.report())
