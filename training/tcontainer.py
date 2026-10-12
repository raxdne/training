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

from abc import ABC, abstractmethod
from typing import final
from statistics import mean

from datetime import timedelta, date, datetime, time, timezone

from suntime import Sun

from icalendar import Calendar, Event, Alarm

import numpy as np

from training import config as config
from training.tdescription import TDescription
from training.ttitle import TTitle
from training.note import Note
from training.unit import Unit
from training.combination import Combination
from training.plot import Plot
from training.phase import Phase

#
#
#

class TContainer(TTitle,TDescription):

    def __init__(self,strArg=None,intArg=None):

        """  """

        super(TTitle, self).__init__()
        super(TDescription, self).__init__()
        #super(Plot, self).__init__()

        self.setTitleStr(strArg)
        self.setDescription()

        self.setPeriod(intArg)

        self.summary = {}
        self.child = []

        self.color = None
        self.tag = []
        self.data = []
        self.summary = {}

        self.dateBegin = None
        self.dateEnd = None
        self.dateFixed = None

        self.setPlan()
        self.setTextOnly()
        self.setPlot()
        #self.setTextOnly(False)
        #self.setVDefaults()
        self.setSkipPattern()

        self.setVDefaults(config.v_defaults)


    def __repr__(self):

        strResult = f'{self.__class__.__name__}([{self.dateBegin!r},{self.dateEnd!r},{self.child!r},{self.periodInt!r}])'
        if self.hasDescription():
            strResult += f'.appendDescription({self.listDescription!r})'
            
        return strResult


    def __str__(self):

        strResult = '\n* ' + self.getTitleString() + ' ' + self.getDateString() + '\n\n'

        strResult += self.getDescriptionString() + '\n\n'

        strResult += self.report()

        return strResult + '\n\n'


    def __len__(self):

        return self.getLength()


    @abstractmethod
    def getLength(self):

        """ return calculated length """

        pass


    @abstractmethod
    def getDuration(self, skipType=None):

        """ return a timedelta """

        pass


    @abstractmethod
    def append(self,objArg):

        """  """

        pass


    @abstractmethod
    def stat(self, dt0=None, dt1=None, skipType=None):

        """ stat all descendant data to self.data and returns it as a nested list  """

        pass


    @abstractmethod
    def updateValues(self,dictArg=None):

        """  """

        pass


    @abstractmethod
    def scale(self,floatScale,patternType=None):

        """  """

        pass


    @final
    def sum(self):

        """ summarize all self.data in self.summary and returns sum of durations in minutes """

        floatResult = 0.0
        self.summary.clear()

        for u in self.data:

            if u[3] not in self.summary:
                self.summary[u[3]] = [[],[]]

            self.summary[u[3]][0].append(u[1])
            self.summary[u[3]][1].append(u[2])

            floatResult += u[2]

        return floatResult


    def schedule(self, argDateOrYear=None, intMonth=None, intDay=None):

        """  """

        if type(argDateOrYear) is bool and argDateOrYear is False:
            # delete all dates
            self.dateFixed = None
            self.dateBegin = None
            self.dateEnd = None
            return self

        if self.dateFixed is not None:
            # keep fixed date and schedule childs
            self.dateBegin = self.dateFixed
            self.dateEnd = self.dateBegin + timedelta(days=(self.periodInt - 1))
        elif type(argDateOrYear) is date:
            self.dateBegin = argDateOrYear
            self.dateEnd = self.dateBegin + timedelta(days=(self.periodInt - 1))
        else:
            try:
                self.dateBegin = date(argDateOrYear, intMonth, intDay)
            except ValueError as e:
                print('error: ' + str(e), file=sys.stderr)
                return self

            self.dateEnd = self.dateBegin + timedelta(days=(self.getLength() - 1))

        d0 = self.dateBegin
        for c in self.child:
            if isinstance(c,TContainer):
                c.schedule(d0)
                d0 += timedelta(days=c.getLength())

        return self


    def setSkipPattern(self,skipType=None):

        """  """

        if hasattr(self,'child'):
            for c in self.child:
                if isinstance(c,TContainer):
                    c.setSkipPattern(skipType)

        self.skipType = skipType

        return self
        

    def setPlot(self,fPlot=False):

        """  """

        for c in self.child:
            try:
                c.setPlot(fPlot)
            except:
                pass

        self.fPlot = fPlot
        
        return self


    def setPlan(self,fPlan=True):

        """  """

        if hasattr(self,'child'):
            for c in self.child:
                if isinstance(c,TContainer):
                    c.setPlan(fPlan)

        self.fPlan = fPlan

        return self


    def isPlan(self):

        """  """

        return self.fPlan


    def setTextOnly(self,fText=True):

        """  """

        self.fText = fText
        
        return self


    def setVDefaults(self,dictArg=None):

        """  """

        if dictArg is not None:
            if config.max_length_type > 0:
                self.v_defaults = {}
                for k in dictArg:
                    # BUG: shorted keys might not be unique
                    self.v_defaults[k[0:config.max_length_type]] = dictArg[k]
            else:
                self.v_defaults = dictArg
        else:
            self.v_defaults = config.v_defaults

        return self


    def resetDistances(self):

        """  """

        self.child.clear()
        self.data.clear()
        #super(Plot, self).__init__()
        #self.strPlotAccumulation = None
        #Plot.__init__(self)

        return self


    @final
    def resetDescription(self):

        """  """

        self.setDescription(None)

        for c in self.child:
            if isinstance(c,TContainer):
                c.resetDescription()

        return self


    def appendChildDescription(self,objArg):

        """  """

        self.child[-1].appendDescription(objArg)

        return self


    def getItem(self,index):

        """ return item of index in TContainer """

        if type(index) is int:
            return self.child[index]
        elif type(index) is list:
            if len(index) == 1:
                return self.child[index[0]]
            elif len(index) > 1:
                return self.child[index[0]].getItem(index[1:])
    
        return None


    def getNumberOfCycles(self):

        """  """

        # TODO: use self.data

        intResult = 0

        if hasattr(self,'child'):
            for c in self.child:
                if type(c) is TContainer:
                    intResult += c.getNumberOfCycles()

        return intResult


    def getMarkers(self, dt0=None, dt1=None):

        """  """

        listResult = []
        
        if hasattr(self,'child'):
            for c in self.child:
                if isinstance(c,TContainer):
                    listResult.extend(c.getMarkers(dt0,dt1))

        return listResult


    def getNumberOfUnits(self, dt0=None, dt1=None):

        """  """

        # TODO: use self.data

        intResult = 0

        if hasattr(self,'set'):
            for c in self.child:
                intResult += c[0]
        elif hasattr(self,'child'):
            for c in self.child:
                if isinstance(c,TContainer):
                    intResult += c.getNumberOfUnits(dt0,dt1)

        return intResult


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
                    print('error: no according TContainer found' + str(objArg), file=sys.stderr)
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

        """  """

        objResult = None

        if objArg is None:
            pass
        elif self.dateBegin is None:
            print('error: date begin', file=sys.stderr)
        elif hasattr(objArg,'child'):
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
            if hasattr(self,'set'):
                # there is no child cycle yet
                delta = objArg.dt.date() - self.dateBegin
                if delta.days > -1 and objArg.dt.date() <= self.dateEnd:
                    l = self.dateEnd - self.dateBegin
                    #print(f'info: new Cycle("{self.getTitleString()}",{l.days + 1}) {self.dateBegin}', file=sys.stderr)
                    c = Cycle(self.getTitleString(), l.days + 1)
                    c.schedule(self.dateBegin)
                    objResult = c.insertByDate(objArg,flagReplace)
                    self.append(c)
            elif hasattr(self,'child'):
                for c in self.child:
                    if isinstance(c,TContainer):
                        objResult = c.insertByDate(objArg,flagReplace)
                        if objResult is not None:
                            break

        return objResult


    def getCycleByDate(self,objDate=None):

        """  """

        return self.getPeriodByDate(objDate)


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
            elif hasattr(self,'child'):
                for c in self.child:
                    if type(c) is TContainer:
                        if c.dateBegin <= objDate.date() and objDate.date() <= c.dateEnd:
                            return c.getPeriodByDate(objDate,intLevel-1)
                return self
        else:
            print('error: no according TContainer found' + str(objDate), file=sys.stderr)

        return None


    def getChildIndexByTitle(self,strArg):

        """  """

        for i in range(len(self.child)):
            if isinstance(self.child[i],TContainer) and self.child[i].getTitleString() == strArg:
                return i
        return -1


    def setPeriod(self, intArg):

        """  """

        if intArg is None:
            self.periodInt = 0
        else:
            self.periodInt = intArg

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
            if type(self.child[i]) is TContainer:
                self.child[i].removeCycles()
            elif hasattr(self,'child'):
                del self.child[i]

        self.data = []

        return self


    def remove(self,patternType=r'.+'):

        """  """

        if hasattr(self,'set'):
            for c in self.child:
                del c
        elif hasattr(self,'child'):
            for c in self.child:
                if isinstance(c,TContainer):
                    c.remove(patternType=patternType)
        elif hasattr(self,'data'):
            l = []
            for d in self.data:
                if re.match(patternType,d[3]):
                    pass
                else:
                    l.append(d)
            self.data = l

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


    @final
    def report(self, dt0=None, dt1=None):

        """  """

        strResult = ''

        if dt0 is not None and dt1 is None:
            if type(dt0) is timedelta:
                #
                return self.report(date.today() - dt0, date.today())
            elif type(dt0) is date:
                #
                return self.report(dt0, date.today())
            else:
                print(f'error: interval {dt0} and {dt1}', file=sys.stderr)
                return strResult
        elif dt0 is not None and dt1 is not None:
            if dt1 < dt0:
                print(f'error: interval {dt0} > {dt1}', file=sys.stderr)
                return self.report(dt1, dt0)
            else:
                p = (dt1 - dt0).days
                strResult += 'Interval (' + str(p) + ' ' + dt0.strftime("%Y-%m-%d") + '/' + dt1.strftime("%Y-%m-%d") + ')\n\n'
        else:
            p = self.getLength()

        n = self.getNumberOfUnits(dt0,dt1)
        #if not self.data and n > 0:
        self.stat(dt0,dt1,self.skipType)

        sum_h = self.sum() / 60
        if sum_h < 0.1:
            return strResult

        for k in sorted(self.summary.keys()):
            # all kinds of units
            sum_k = sum(self.summary[k][1]) / 60.0
            sum_d = sum(self.summary[k][0])

            if sum_k > 0.01:
                strResult += ("{:4} x {:" + str(config.max_length_type) + "} ").format(len(self.summary[k][0]), k)

                if not self.summary[k][0]:
                    strResult += ("{:7}    {:7.01f} h {:.02f}\n").format(' ',
                                                                         sum_k,
                                                                         sum_k / sum_h)
                elif len(self.summary[k][0]) < 3:
                    strResult += ("{:7.01f} {} {:7.01f} h {:.02f}\n").format(sum_d,
                                                                             config.unit_distance,
                                                                             sum_k,
                                                                             sum_k / sum_h)
                else:
                    strResult += ("{:7.01f} {} {:7.02f} {} {:7.01f} h {:.02f} {:5.01f} /{:5.01f} /{:5.01f}\n").format(sum_d,
                                                                                                                      config.unit_distance,
                                                                                                                      sum_d / p * 7.0,
                                                                                                                      config.unit_distance + '/Week',
                                                                                                                      sum_k,
                                                                                                                      sum_k / sum_h,
                                                                                                                      min(self.summary[k][0]),
                                                                                                                      mean(self.summary[k][0]),
                                                                                                                      max(self.summary[k][0]))

        if n > 0:
            strResult += "\n{} Units {:.1f} h in {} Days ≌ {:.2f} h/Week ≌ {:.0f} min/d\n".format(n, sum_h, p, sum_h * 7.0 / p, sum_h * 60 / p)

        return strResult


    @final
    def dup(self):

        """  """

        return copy.deepcopy(self)


    def toString(self):

        """  """

        return str(self)


    def toHtmlTableOfContent(self,strIndent=''):

        """  """

        strResult = self.getTitleLineTableOfContent(strIndent) + self.getDateString() + '\n'

        if hasattr(self,'child'):
            for c in self.child:
                if type(c) is TContainer:
                    strResult += c.toHtmlTableOfContent(strIndent + '    ')

        return strResult


    def toHtmlFile(self):

        """ returns html/body + content """

        strResult = '<!doctype html public "-//IETF//DTD HTML 4.0//EN">'

        strResult += "<html>"

        strResult += "<head>"

        strResult += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>'

        strResult += f'<title>{self.getTitleXML()}</title>'

        strResult += config.style

        strResult += config.script

        strResult += "</head>\n<body>\n"

        strResult += f'<h1>{self.getTitleXML()}</h1>'

        if not self.fText:
            strResult += '<div style="text-align: center;margin: 40px;">' + self.toSVGGanttChart() + '</div>\n'
        else:
            strResult += '<pre>' + self.toHtmlTableOfContent() + '</pre>\n'

        strResult += self.toHtml()

        if not self.fText:
            strResult += f'<section {config.getClass(__name__)}>'
            strResult += '<div class="header">' + self.getTitleXML() + self.getDateString() + '</div>\n'
            strResult += '<div style="text-align: center;margin: 40px;">' + self.toSVGDiagram() + '</div>\n'
            strResult += '</section>\n'

        strResult += config.footer

        strResult += "</body>\n</html>"

        return strResult


    def toCSV(self):

        """  """

        strResult = ""
        if self.dateBegin is not None:
            strResult += self.dateBegin.strftime("%Y-%m-%d")
        strResult += ';;;;TContainer "{}" {}\n\n'.format(self.getTitleString(), self.getDateString())

        if hasattr(self,'child'):
            for c in self.child:
                strResult += c.toCSV()
            strResult += '\n'

        return strResult


    def toFreeMind(self):

        """  """

        strResult = '<?xml version="1.0" encoding="UTF-8"?>\n<map>\n'
        strResult += self.toFreemindNode()
        strResult += '</map>\n'

        return strResult


    def toSqlite(self):

        """  """

        strResult = ''
        
        if hasattr(self,'child'):
            for c in self.child:
                if isinstance(c,TContainer):
                    strResult += c.toSqlite()

        return strResult


    def toSqliteDump(self):

        """  """

        strResult = 'PRAGMA journal_mode = OFF;\n\n'

        strResult += """CREATE TABLE IF NOT EXISTS "queries" (query text, "description"	TEXT);

        INSERT INTO 'queries' VALUES (\"SELECT * FROM units;\",\"find all units\");
        INSERT INTO 'queries' VALUES (\"SELECT count() AS Count, type AS Type FROM units GROUP BY type ORDER BY Count DESC;\",\"count the units\");
        INSERT INTO 'queries' VALUES (\"SELECT sum(dist) AS Sum, type AS Type FROM units GROUP BY type ORDER BY Sum DESC;\",\"summarize all distances\");\n\n"""

        strResult += """CREATE TABLE IF NOT EXISTS "units" (
	"date"	TEXT,
	"dist"	REAL,
	"type"	TEXT,
	"duration"	TEXT,
	"description"	TEXT
        );\n\n"""

        strResult += self.toSqlite()

        return strResult


    def toSVGDiagram(self):

        """ returns SVG code for a vertical timeline """

        diagram_height = self.getLength() * (config.diagram_bar_height * 2) + 100
        strResult = '<svg baseProfile="full" height="{}" version="1.1" width="{}" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink">'.format(diagram_height, config.diagram_width)

        strResult += '<style type="text/css">svg { font-family: ' + config.font_family + '; font-size: ' + str(config.font_size) + 'pt; }</style>'

        #strResult += '<g transform="rotate(90)">'
        #'<text x="210" y="110">TContainer 2.2021</text>

        for i in [3600/4,3600/2,3600,2*3600,3*3600,4*3600,5*3600,6*3600]:
            w = i / 3600 * 25 * config.diagram_scale_dist
            strResult += '<line stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format( config.diagram_offset + w, 20, config.diagram_offset + w, diagram_height)

        strResult += '<g>'
        for t in self.tag:
            if type(t) is Phase:
                y_i = ((t.date - self.dateBegin).days + 1) * config.diagram_bar_height * 2
                strResult += '<rect id="{}" fill="{}" opacity=".5" stroke="none" stroke-width=".5" x="{}" y="{}" height="{}" width="{}" rx="2">\n'.format(str(id(t)), t.color, 0, y_i + 3, t.duration * config.diagram_bar_height * 2 + 2, config.diagram_width)
                strResult += f'<title>{t.title} ({t.duration} {t.date.strftime("%Y-%m-%d")} {(t.date + timedelta(days=t.duration - 1)).strftime("%Y-%m-%d")})</title>\n'
                strResult += '</rect>'
        strResult += '</g>'

        strResult += self.toSVG()
        #strResult += '</g>'
        strResult += '</svg>\n'

        return strResult


    def toVCalendar(self):

        """  """

        cal = Calendar()
        cal.add('prodid', '-//{title}//  //'.format(title=self.getTitleString()))
        cal.add('version', '2.0')
        self.to_ical(cal)
        return cal.to_ical()


    def writeFiles(self, strDirArg, strId):

        Path(strDirArg).mkdir(parents=True,exist_ok=True)

        #periodArg.plotHist(strDirArg + '/' + strId + '-hist.svg')
        #periodArg.plotTimeDist(strDirArg + '/' + strId + '-ts.svg')

        f = open(strDirArg + '/' + strId + '.ics', 'wb')
        f.write(self.toVCalendar())
        f.close()

        #f = open(strDirArg + '/' + strId + '.csv', 'w')
        #f.write(periodArg.toCSV())
        #f.close()

        f = open(strDirArg + '/' + strId + '-periods.html', 'w')
        f.write(self.toHtmlFile())
        f.close()
        return
        f = open(strDirArg + '/' + strId + '-dashboard.html', 'w')
        f.write(self.toComparisonHtmlFile())
        f.close()

        f = open(strDirArg + '/' + strId + '-gantt.svg', 'w')
        f.write(self.toSVGGanttChart())
        f.close()

        f = open(strDirArg + '/' + strId + '.svg', 'w')
        f.write(self.toSVGDiagram())
        f.close()

        f = open(strDirArg + '/' + strId + '.mm', 'w')
        f.write(self.toFreeMind())
        f.close()

        f = open(strDirArg + '/' + strId + '.sqlite', 'w')
        f.write(self.toSqliteDump())
        f.close()

        #f = open(strDirArg + '/' + strId + '.py', 'w')
        #f.write(repr(self))
        #f.close()

        index = '<!doctype html public "-//IETF//DTD HTML 4.0//EN">'

        index += f'<html><head><title>{strId}: {self.getTitleXML()}</title>'

        index += config.style
        #index += config.script

        index += f'<h1>{self.getTitleXML()}</h1>'

        index += f'<p><img src="{strId}-gantt.svg"/></p>\n'

        index += "<ul>\n"
        index += f'<li><a href=".">..</a></li>'
        index += f'<li><a href="{strId}-periods.html">{strId} page</a></li>'
        index += f'<li><a href="{strId}-dashboard.html">{strId} dashboard</a></li>'
        index += f'<li><a href="{strId}-gantt.svg">{strId} Gantt</a> (can be edited in <a target="_blank" href="https://inkscape.org/">Inkscape</a>)</li>'
        index += f'<li><a href="{strId}.svg">{strId} Timeline</a></li>'
        index += f'<li><a href="{strId}.ics">{strId} Calendar file</a> (for use in <a target="_blank" href="https://www.thunderbird.net/">Thunderbird</a> etc.)</li>'
        index += f'<li><a href="{strId}.mm">{strId} Mindmap file</a> (for use in <a target="_blank" href="https://docs.freeplane.org/">Freemind/Freeplan</a>)</li>'
        index += '</ul>'
        
        index += config.footer

        index += '</body></html>'

        f = open(strDirArg + '/' + strId + '.html', 'w')
        f.write(index)
        f.close()


