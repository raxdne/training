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
from training.tcontainer import TContainer

from training.note import Note
from training.unit import Unit
from training.combination import Combination
#from training.plot import Plot
from training.phase import Phase
from training.cycle import Cycle
from training.bunch import Bunch

#
#
#

class Period(TContainer):

    def __init__(self,strArg=None,intArg=None):

        """  """

        super().__init__(strArg,intArg)


    def __str__(self):

        strResult = super().__str__()

        for c in self.child:
            strResult += f'{c}\n'

        return strResult + '\n\n'


    def updateValues(self,dictArg=None):

        """  """

        for c in self.child:
            if isinstance(c,TContainer):
                c.updateValues(self.v_defaults)

        return self


    def resetDistances(self):

        """  """

        super().resetDistances()

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

        # TODO: use self.data

        intResult = 0

        for c in self.child:
            if isinstance(c,TContainer):
                intResult += c.getNumberOfCycles()

        return intResult


    def getMarkers(self, dt0=None, dt1=None):

        """  """

        listResult = []

        for c in self.child:
            if type(c) is Cycle or type(c) is Period:
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


    def append(self,objArg):

        """ reset data collection of period  """

        self.data.clear()
        self.summary.clear()

        if objArg is None:
            print('error: ' + str(objArg), file=sys.stderr)
        elif type(objArg) is list:
            for a in objArg:
                self.append(a)
        elif isinstance(objArg,TContainer) or isinstance(objArg,Note):
            self.child.append(objArg.dup())
            self.periodInt += objArg.getLength()
            #self.schedule()
        else:
            print('error: ' + str(objArg), file=sys.stderr)

        return self


    def insert(self,objArg,intLevel=-1):

        """  """

        objResult = self

        if objArg is None:
            print('error: object', file=sys.stderr)
        elif self.dateBegin is None:
            print('error: date begin', file=sys.stderr)
        elif isinstance(objArg,TContainer):
            if objArg.dateBegin is None:
                print('error: date begin', file=sys.stderr)
            else:
                p = self.getPeriodByDate(objArg.dateBegin,intLevel)
                if p is None:
                    print('error: no according period found' + str(objArg), file=sys.stderr)
                elif not p.child:
                    p.child.append(objArg.dup())
                else:
                    for i in range(len(p.child)):
                        if isinstance(p.child[i],TContainer):
                            if p.child[i].dateBegin == objArg.dateBegin:
                                # begin is equal
                                p.child.insert(i,objArg.dup())
                                break
                            elif p.child[i].dateEnd >= objArg.dateBegin:
                                # objArg begins in p.child[i]
                                p.child[i].cutAfter(objArg.dateBegin - timedelta(days=1))
                                p.child.insert(i+1,objArg.dup())
                                break
                            elif p.child[i] == p.child[-1]:
                                print('error: no cycle found', file=sys.stderr)
                                p.child.append(objArg.dup())
                self.schedule()
        elif type(objArg) is Note or type(objArg) is Unit or type(objArg) is Combination:
            if objArg.dt is None:
                print('error: date', file=sys.stderr)
            else:
                c = self.getCycleByDate(objArg.dt)
                if c is None or not c.child:
                    print('error: no cycle found', file=sys.stderr)
                else:
                    # is inside this Cycle
                    j = round((objArg.dt.date() - c.dateBegin).total_seconds() / (24 * 60 * 60))
                    c.insert(j,objArg.dup())
                self.schedule()

        return objResult


    def insertByDate(self,objArg,flagReplace=False):

        """ BUG: """

        objResult = None

        if objArg is None:
            pass
        elif self.dateBegin is None:
            print('error: date begin', file=sys.stderr)
        elif type(objArg) is Cycle:
            d = 0
            for v in objArg.child:
                if not v:
                    # day without elements
                    if flagReplace:
                        # create a scheduled empty unit to overwrite
                        u = Unit()
                        u.setDate(objArg.dateBegin + timedelta(days=d))
                        self.insertByDate(u,True)
                else:
                    for u in v:
                        if type(u) is Unit or type(u) is Combination:
                            self.insertByDate(u,flagReplace)
                        else:
                            print('error: type ' + str(type(u)), file=sys.stderr)
                d += 1

            if flagReplace:
                c = self.getCycleByDate(objArg.dateBegin)
                if c is not None:
                    if objArg.hasTitle():
                        # copy title from objArg to c
                        c.setTitleStr(objArg.getTitleString())
                    if objArg.hasDescription():
                        # copy description from objArg to c
                        c.setDescription(objArg.getDescription())
                # TODO: handle multiple affected cycles
                # TODO: transfer color etc

        elif objArg is not None and objArg.dt is not None:
            if not self.child:
                # there is no child cycle yet
                delta = objArg.dt.date() - self.dateBegin
                if delta.days > -1 and objArg.dt.date() <= self.dateEnd:
                    l = self.dateEnd - self.dateBegin
                    #print(f'info: new Cycle("{self.getTitleString()}",{l.days + 1}) {self.dateBegin}', file=sys.stderr)
                    c = Cycle(self.getTitleString(), l.days + 1)
                    c.schedule(self.dateBegin)
                    objResult = c.insertByDate(objArg,flagReplace)
                    self.append(c)
            else:
                for c in self.child:
                    if isinstance(c,TContainer):
                        objResult = c.insertByDate(objArg,flagReplace)
                        if objResult is not None:
                            break

        return objResult


    def fill(self,objArg,floatProgression=1.0):

        """  """

        flagReplace=False
        objResult = self

        if objArg is None:
            print('error: undefined object ' + str(objArg), file=sys.stderr)
        elif type(objArg) is list and objArg:
            for u in objArg:
                self.insert(u,flagReplace)
        elif isinstance(objArg,TContainer) or type(objArg) is Unit or type(objArg) is Combination:
            for c in self.child:
                if isinstance(c,TContainer):
                    c.fill(objArg,floatProgression)
        else:
            print(f'error: filling {type(objArg)} of {len(self.child)} {objArg}', file=sys.stderr)

        return objResult


    def getCycleByDate(self,objDate=None):

        """  """

        if objDate is None:
            return self.getCycleByDate(datetime.now())
        elif type(objDate) is str:
            return self.getCycleByDate(datetime.fromisoformat(objDate))
        elif type(objDate) is date:
            return self.getCycleByDate(datetime.combine(objDate,time(0)))
        elif type(objDate) is datetime:
            for c in self.child:
                if type(c) is Period:
                    if c.dateBegin <= objDate.date() and objDate.date() <= c.dateEnd:
                        return c.getCycleByDate(objDate)
                elif type(c) is Cycle:
                    r = c.getCycleByDate(objDate)
                    if r is not None:
                        return r

        return None


    def getPeriodByDate(self,objDate=None,intLevel=0):

        """  """

        if objDate is None:
            return self.getPeriodByDate(datetime.now(),intLevel)
        elif type(objDate) is str:
            return self.getPeriodByDate(datetime.fromisoformat(objDate),intLevel)
        elif type(objDate) is date:
            return self.getPeriodByDate(datetime.combine(objDate,time(0)),intLevel)
        elif type(objDate) is datetime:
            if not self.child or intLevel < 1:
                if self.dateBegin <= objDate.date() and objDate.date() <= self.dateEnd:
                    return self
            else:
                for c in self.child:
                    if type(c) is Period:
                        if c.dateBegin <= objDate.date() and objDate.date() <= c.dateEnd:
                            return c.getPeriodByDate(objDate,intLevel-1)
                return self
        else:
            print('error: no according period found' + str(objDate), file=sys.stderr)

        return None


    def getChildIndexByTitle(self,strArg):

        """  """

        for i in range(len(self.child)):
            if isinstance(self.child[i],TContainer) and self.child[i].getTitleString() == strArg:
                return i
        return -1


    def scale(self,floatScale,patternType=None):

        """  """

        if floatScale > 0.01 and  abs(floatScale - 1.0) > 0.01:
            for c in self.child:
                if isinstance(c,TContainer):
                    c.scale(floatScale,patternType)

            self.summary.clear()

        return self


    def overwrite(self,argCycle,argDate=None):

        """ overwrite the descendant cycle sequence by argCycle """

        if type(argCycle) is Cycle:
            if argDate:
                c = self.getCycleByDate(argDate)
                if type(c) is Cycle:
                    c.insert((argDate - c.dateBegin).days,argCycle,True)
            elif argCycle.dateBegin:
                self.overwrite(argCycle,argCycle.dateBegin)
            else:
                self.overwrite(argCycle, self.dateBegin)
        else:
            print(f'error: inserting {type(argCycle)} at date {argDate}', file=sys.stderr)

        return self


    def swap(self,argA,argB):

        """ swap childs """

        if type(argA) is int and type(argB) is int:
            if argA > -1 and argA < len(self.child) and argB > -1 and argB < len(self.child):
                self.child[argA], self.child[argB] = self.child[argB], self.child[argA]
        elif type(argA) is str and type(argB) is str:
            self.swap(self.getChildIndexByTitle(argA),self.getChildIndexByTitle(argB))
        
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


    def remove(self,patternType=r'.+'):

        """  """

        for c in self.child:
            if isinstance(c,TContainer):
                c.remove(patternType=patternType)

        self.summary.clear()

        return self


    def cut(self, d0, d1):

        """  """

        return self.cutBefore(d0).cutAfter(d1)


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
            self.data.clear()
            self.summary.clear()

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
            self.data.clear()
            self.summary.clear()

        return self


    def fix(self, objArg):

        """  """

        if self.dateFixed is not None:
            # keep fixed date
            pass
        #elif self.dateBegin is None or self.dateEnd is None:
        #    pass
        #elif objArg is not None and type(objArg) is date and self.dateBegin <= objArg and objArg <= self.dateEnd:
        elif objArg is not None and type(objArg) is date:
            self.dateFixed = objArg

        self.schedule()

        return self


    def addTags(self, objArg=None):

        """  """

        if type(objArg) is list:
            self.tag.extend(objArg)
        elif type(objArg) is Phase:
            self.tag.append(objArg)

        return self


    def stat(self, dt0=None, dt1=None, skipType=None):

        """ stat all descendant data to self.data and returns it as a nested list  """

        self.data.clear()
        self.summary.clear()

        if skipType is None:
            skipType = self.skipType
        for c in self.child:
            if isinstance(c,TContainer):
                self.data.extend(c.stat(dt0,dt1,skipType))

        return self.data


    def parseFile(self,listFilename,fUpdater=None):

        """  """

        if type(listFilename) is str:
            listFilename = [listFilename]

        a = []
        d0 = None
        d1 = None
        t = Unit()
        n = Note()

        for filename in listFilename:
            print("* ",filename, file=sys.stderr)
            with open(filename) as f:
                content = f.read().splitlines()
            f.close()

            d_i = None
            for l in content:
                if l is None or l == '' or re.match(r"^sep",l) or re.match(r"^\*",l):
                    pass
                elif (fUpdater is not None and t.parse(fUpdater(l))) or t.parse(l):
                    if t.dt is not None:
                        d_i = t.dt
                        if d0 is None or t.dt < d0:
                            d0 = t.dt
                        if d1 is None or t.dt > d1:
                            d1 = t.dt
                    else:
                        t.dt = d_i

                    a.append(t)
                    t = Unit()
                elif (fUpdater is not None and n.parse(fUpdater(l))) or n.parse(l):
                    if n.dt is not None:
                        d_i = n.dt
                        if d0 is None or n.dt < d0:
                            d0 = t.dt
                        if d1 is None or n.dt > d1:
                            d1 = t.dt
                    else:
                        n.dt = d_i

                    a.append(n)
                    n = Note()
                else:
                    print('error: ' + l, file=sys.stderr)

                if d1 is None and d0 is not None:
                    d1 = d0

        if d0 is None:
            print('error: No start date found', file=sys.stderr)
        elif d1 is None:
            print('error: No end date found', file=sys.stderr)
        else:
            delta = d1 - d0

            if hasattr(self,'child'):
                # there is a child list already
                pass
            elif delta.days < 365:
                for y in range(d0.year,d1.year+1):
                    self.append(Period('').CalendarWeekPeriod(y))
            elif delta.days < 3 * 365:
                for y in range(d0.year,d1.year+1):
                    self.append(Period('').CalendarMonthPeriod(y))
            else:
                for y in range(d0.year,d1.year+1):
                    self.append(Period('').CalendarYearPeriod(y))

            for t in a:
                c = self.getCycleByDate(t.dt)
                if c is not None:
                    c.insertByDate(t)

        self.setPlan(False)
        return self


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


    def toHtmlTableOfContent(self,strIndent=''):

        """  """

        strResult = self.getTitleLineTableOfContent(strIndent) + self.getDateString() + '\n'

        for c in self.child:
            if type(c) is Period:
                strResult += c.toHtmlTableOfContent(strIndent + '    ')
            elif type(c) is Cycle:
                strResult += c.getTitleLineTableOfContent(strIndent + '    ') + '\n'

        return strResult


    def toComparisonHtmlFile(self, listArg=[]):

        """ returns html/body + content """

        strResult = '<!doctype html public "-//IETF//DTD HTML 4.0//EN">'

        strResult += "<html>"

        strResult += "<head>"

        strResult += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>'

        strResult += "<title></title>"

        strResult += config.style

        strResult += "</head>\n<body>\n"

        if not listArg:
            l = self.child
        else:
            l = listArg

        for c in l:
            if isinstance(c,TContainer):
                strResult += f'<section {config.getClass(__name__)} id="{str(id(c))}"'

                strResult += '<div class="header">' + c.getTitleXML()
                if c.dateBegin is not None and c.dateEnd is not None:
                    strResult += c.getDateString()
                strResult += '</div>\n'

                strResult += '<pre>' + c.report() + '</pre>'

                if c.fPlot and (isinstance(c,TContainer) and c.getNumberOfCycles() > 0):
                    strResult += '<div>'
                    strResult += c.plotAccumulationDuration()
                    strResult += c.plotAccumulation()
                    strResult += c.plotHist()
                    strResult += c.plotTimeDist()
                    strResult += c.toSVGGanttChart()
                    #strResult += c.toSVGDiagram()
                    strResult += '</div>'

                strResult += '</section>\n'

        strResult += config.footer

        strResult += "</body>\n</html>"

        return strResult


    def toComparisonHtmlTableFile(self, listArg=[]):

        """ returns html/body + content """

        strResult = '<!doctype html public "-//IETF//DTD HTML 4.0//EN">'

        strResult += "<html>"

        strResult += "<head>"

        strResult += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>'

        strResult += "<title></title>"

        strResult += config.style

        strResult += "</head>\n<body>\n"

        if not listArg:
            l = self.child
        else:
            l = listArg

        strResult += "<table style='border: none;'><thead/>\n<tbody>\n"

        strResult += "<tr>\n"
        
        for c in l:
            if isinstance(c,TContainer):
                strResult += "<td class='graph'>\n"
                #strResult += '<section class="{}" id="{}">'.format(__name__, str(id(c)))

                strResult += '<div class="header">' + c.getTitleXML()
                if c.dateBegin is not None and c.dateEnd is not None:
                    strResult += c.getDateString()
                strResult += '</div>\n'

                strResult += '<pre>' + c.report() + '</pre>'
                strResult += "</td>\n"

        strResult += "</tr>\n"

        strResult += "<tr>\n"

        for c in l:
            if isinstance(c,TContainer):
                strResult += "<td class='graph'>\n"
                strResult += c.plotAccumulationDuration()
                strResult += "</td>\n"

        strResult += "</tr>\n"

        strResult += "<tr>\n"

        for c in l:
            if isinstance(c,TContainer):
                strResult += "<td class='graph'>\n"
                strResult += c.plotAccumulation()
                strResult += "</td>\n"

        strResult += "</tr>\n"

        strResult += "<tr>\n"

        for c in l:
            if isinstance(c,TContainer):
                strResult += "<td class='graph'>\n"
                strResult += c.plotHist()
                strResult += "</td>\n"

        strResult += "</tr>\n"

        strResult += "<tr>\n"

        for c in l:
            if isinstance(c,TContainer):
                strResult += "<td class='graph'>\n"
                strResult += c.plotTimeDist()
                strResult += "</td>\n"

        strResult += "</tr>\n"

        strResult += "<tr>\n"

        for c in l:
            if isinstance(c,TContainer):
                strResult += "<td class='graph'>\n"
                strResult += c.toSVGGanttChart()
                strResult += "</td>\n"

        strResult += "</tr>\n"

        strResult += "</tbody>\n</table>\n"
        strResult += config.footer
        strResult += "</body>\n</html>"

        return strResult


    def toCSV(self):

        """  """

        strResult = ""
        if self.dateBegin is not None:
            strResult += self.dateBegin.strftime("%Y-%m-%d")
        strResult += ';;;;Period "{}" {}\n\n'.format(self.getTitleString(), self.getDateString())

        for c in self.child:
            strResult += c.toCSV()
        strResult += '\n'

        return strResult


    def toFreemindNode(self):

        """  """

        strResult = '<node'
        if self.color is not None:
           strResult += ' BACKGROUND_COLOR="{}"'.format(self.color)
        elif self.getNumberOfUnits() < 1:
           strResult += ' BACKGROUND_COLOR="{}"'.format('#ffaaaa')
        else:
            strResult += ' FOLDED="{}"'.format('false')

        strResult += ' LOCALIZED_STYLE_REF="default" TEXT="' + self.getTitleXML()
        if self.dateBegin is not None and self.dateEnd is not None:
            strResult += ' ' + self.getDateString() + '&#xa;' + self.report().replace('\n','&#xa;')
        strResult += '">\n'

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
            if type(c) is Cycle or type(c) is Period:
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
            if type(t) is Phase:
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
            event.add('summary', 'Period: {}'.format(self.getTitleString()))
            event.add('dtstart', self.dateBegin)
            event.add('dtend', self.dateEnd + timedelta(days=1))
            event.add('dtstamp', datetime.now().astimezone(None))
            cal.add_component(event)

        else:
            fOutput = False
            for c in self.child:
                c.to_ical(cal)
                if type(c) is Cycle:
                    # output only, if there is a Cycle child involved
                    fOutput = True

            if fOutput and self.dateBegin is not None and self.hasTitle():
                event = Event()
                event.add('summary', 'Begin Period: ' + self.getTitleString())
                event.add('dtstart', self.dateBegin)
                event.add('dtend', self.dateBegin + timedelta(days=1))
                event.add('dtstamp', datetime.now().astimezone(None))
                cal.add_component(event)

            if fOutput and self.dateEnd is not None and self.hasTitle():
                event = Event()
                event.add('summary', 'End Period: ' + self.getTitleString())
                event.add('dtstart', self.dateEnd)
                event.add('dtend', self.dateEnd + timedelta(days=1))
                event.add('dtstamp', datetime.now().astimezone(None))
                cal.add_component(event)


    def toVCalendar(self):

        """  """

        cal = Calendar()
        cal.add('prodid', '-//{title}//  //'.format(title=self.getTitleString()))
        cal.add('version', '2.0')
        self.to_ical(cal)
        return cal.to_ical()


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
