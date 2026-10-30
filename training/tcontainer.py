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
import re

from abc import ABC, abstractmethod
from typing import final
from statistics import mean

from datetime import timedelta, date, datetime, time, timezone
from suntime import Sun
from icalendar import Calendar, Event, Alarm
import numpy as np

from training import config as config
from training.tcore import TCore
from training.titem import TItem

from training.phase import Phase

#
#
#

class TContainer(TCore):

    def __init__(self,t=None,l=0):

        """  """

        super().__init__(t)
        self.periodInt = l

        self.child = []

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
        self.setVDefaults()
        self.setSkipPattern()

        self.setVDefaults(config.v_defaults)


    def __repr__(self):

        strResult = f'{self.__class__.__name__}([{self.dateBegin!r},{self.dateEnd!r},{self.child!r},{self.periodInt!r}])'
        if self.hasDescription():
            strResult += f'.appendDescription({self.description!r})'
            
        return strResult


    def __str__(self):

        strResult = '\n* ' + self.title + ' ' + self.getDateString() + '\n\n'

        strResult += self.getDescriptionString() + '\n\n'

        strResult += self.report()

        return strResult + '\n\n'


    def __len__(self):

        return self.getLength()


    def __enter__(self):

        """  """

        return self.child


    def __exit__(self, exc_type, exc_value, exc_tb):    

        """  """

        pass        


    @abstractmethod
    def getLength(self):

        """ return calculated length """

        pass


    @abstractmethod
    def getDuration(self, skipType=None):

        """ return a timedelta """

        pass


    @abstractmethod
    def append(self,o):

        """ append objects to the list of childs """

        pass


    @abstractmethod
    def extend(self,n=7):

        """ append last n days at the end """

        pass


    def reverse(self):

        """  """

        r = self.dup()
        r.child.reverse()
        
        return r


    @final
    def cut(self, d0, d1):

        """  """

        return self.cutBefore(d0).cutAfter(d1)


    @abstractmethod
    def cutBefore(self,d):

        """  """

        pass


    @abstractmethod
    def cutAfter(self,d):

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
    def scale(self,f,p=None):

        """ returns a copy of self, scaled by f and matching pattern p if not None """

        pass


    @final
    def sum(self):

        """ summarize all self.data in self.summary and returns sum of durations in minutes """

        r = 0.0
        self.summary.clear()

        for u in self.data:

            if u[3] not in self.summary:
                self.summary[u[3]] = [[],[]]

            self.summary[u[3]][0].append(u[1])
            self.summary[u[3]][1].append(u[2])

            r += u[2]

        return r


    def schedule(self, argDateOrYear=None, intMonth=1, intDay=1):

        """  """

        if argDateOrYear is None or (type(argDateOrYear) is bool and argDateOrYear is False):
            # delete all dates
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


    def clean(self):

        """ resets all statistics """

        self.data.clear()
        self.summary.clear()

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


    @abstractmethod
    def resetDistances(self):

        """  """

        pass


    @final
    def resetDescription(self):

        """  """

        self.setDescription(None)

        for c in self.child:
            if isinstance(c,TContainer):
                c.resetDescription()

        return self


    def appendChildDescription(self,o):

        """  """

        self.child[-1].appendDescription(o)

        return self


    def getDateString(self):

        """  """

        strResult = ' '

        if type(self.dateBegin) is date and self.dateBegin is not None and type(self.dateEnd) is date and self.dateEnd is not None:
            strResult += '(' + str((self.dateEnd - self.dateBegin).days + 1) + ' ' + self.dateBegin.strftime("%Y-%m-%d") + '/' + self.dateEnd.strftime("%Y-%m-%d") + ')'

        return strResult


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
                    print('error: no according TContainer found' + str(o), file=sys.stderr)
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


    @abstractmethod
    def insertByDate(self,o,f=False):

        """  """

        pass


    @final
    def isDateInContainer(self,dt=None):

        """ returns True if dt is between self.dateBegin and self.dateEnd """

        if type(dt) is datetime:
            return self.isDateInContainer(dt.date())
        
        if not isinstance(dt,date):
            return False

        return (self.dateBegin is not None and self.dateEnd is not None and self.dateBegin <= dt and dt <= self.dateEnd)


    @final
    def query(self,**kwargs):
        
        """ """
        
        if 'level' not in kwargs:
            kwargs['level'] = 1
            return self.query(**kwargs)

        if kwargs['level'] < 1:
            return []
        
        kwargs['level'] -= 1
        
        r = []
        for i in range(len(self.child)):
            if ('date' not in kwargs or self.child[i].isDateInContainer(kwargs['date'])) and ('index' not in kwargs or (isinstance(kwargs['index'],int) and i == kwargs['index']) or (isinstance(kwargs['index'],list) and (i in kwargs['index']))):
                if ('type' not in kwargs or isinstance(self.child[i],kwargs['type'])):
                    r.append(self.child[i])
                if isinstance(self.child[i],TContainer):
                    l = self.child[i].query(**kwargs)
                    if len(l) > 0:
                        r.extend(l)
        return r                    


    @final
    def qy(self,**kwargs):
        
        """ flexible query method (index | date, type, level) """

        if 'index' in kwargs:
            # search using index
            if isinstance(kwargs['index'],list):
                if len(kwargs['index']) > 0:
                    i = kwargs['index'].pop(0)

                if len(kwargs['index']) > 0:
                    yield from self.child[i].qy(**kwargs)
                else:
                    yield self.child[i]

            elif isinstance(kwargs['index'],int):
                yield self.child[kwargs['index']]

        else:
            # search using date, level and type
            if 'level' in kwargs:
                if kwargs['level'] < 0:
                    return
                else:
                    kwargs['level'] -= 1

            for i in range(len(self.child)):
                if isinstance(self.child[i],TContainer):
                    if 'date' not in kwargs or kwargs['date'] is None or self.child[i].isDateInContainer(kwargs['date']):
                        if 'type' not in kwargs or isinstance(self.child[i],kwargs['type']):
                            yield self.child[i]

                    yield from self.child[i].qy(**kwargs)


    @final
    def getContainerByDate(self,objDate=None,intLevel=10):

        """ returns the TContainer where the objDate is in and intLevel """

        if objDate is None:
            return self.getContainerByDate(datetime.now(),intLevel)
        elif type(objDate) is str:
            return self.getContainerByDate(datetime.fromisoformat(objDate),intLevel)
        elif type(objDate) is date:
            return self.getContainerByDate(datetime.combine(objDate,time(0)),intLevel)
        elif type(objDate) is datetime:
            if self.isDateInContainer(objDate):
                if intLevel < 1:
                    pass
                else:
                    for c in self.child:
                        if isinstance(c,TContainer):
                            r = c.getContainerByDate(objDate,intLevel-1)
                            if r is not None:
                                return r
                return self
        else:
            print('error: no according TContainer found' + str(objDate), file=sys.stderr)

        return None


    @property
    def periodInt(self):

        """  """

        return self._period.days


    @periodInt.setter
    def periodInt(self, *args, **kwargs):

        """  """

        self._period = timedelta(*args, **kwargs)


    def setPeriod(self, l=None):

        """  """

        self.periodInt = l

        return self


    def swap(self,a,b):

        """  """

        if a > -1 and b > -1 and a < len(self.child) and b < len(self.child) and a != b:
            self.child[b], self.child[a] = self.child[a], self.child[b]

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


    @abstractmethod
    def remove(self,p=None):

        """  """

        pass


    def addTags(self, o=None):

        """  """

        if type(o) is list:
            self.tag.extend(o)
        elif type(o) is Phase:
            self.tag.append(o)

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


    def toString(self):

        """  """

        return str(self)


    @abstractmethod
    def toHtmlTable(self):

        """  """
        
        pass


    @final
    def toHtmlTableOfContent(self,strIndent=''):

        """  """

        strResult = f'{strIndent}<a href="#{str(id(self))}">{self.getTitleXML()}</a>' + self.getDateString() + '\n'

        for c in self.child:
            if isinstance(c,TContainer):
                strResult += c.toHtmlTableOfContent(strIndent + '    ')

        return strResult


    @final
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
        strResult += ';;;;TContainer "{}" {}\n\n'.format(self.title, self.getDateString())

        if hasattr(self,'child'):
            for c in self.child:
                strResult += c.toCSV()
            strResult += '\n'

        return strResult


    def toFreemindNodeAttr(self):

        """  """

        strResult = ''

        if self.color is not None:
            strResult += f' BACKGROUND_COLOR="{self.color}"'
        elif self.getNumberOfUnits() < 1:
            strResult += ' BACKGROUND_COLOR="#ffaaaa"'
        else:
            strResult += ' FOLDED="true"'

        strResult += ' LOCALIZED_STYLE_REF="default" TEXT="' + self.getTitleXML() + ' ' + self.getDateString() + '&#xa;' + self.report().replace('\n','&#xa;') + '"'

        return strResult


    @final
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
        cal.add('prodid', '-//{title}//  //'.format(title=self.title))
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

        f = open(strDirArg + '/' + strId + '.mm', 'w')
        f.write(self.toFreeMind())
        f.close()

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


