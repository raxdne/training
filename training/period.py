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

import sys

import math

import copy

import re

from statistics import mean

from datetime import timedelta, date, datetime, time, timezone

from suntime import Sun

from icalendar import Calendar, Event, Alarm

import matplotlib.pyplot as plt
import numpy as np

from training import config as config
from training.description import Description
from training.title import Title
from training.note import Note
from training.unit import Unit
from training.cycle import Cycle
from training.combination import Combination
from training.plot import Plot

#
#
#

class Period(Title,Description,Plot):

    def __init__(self,strArg=None,intArg=None):

        """  """

        super(Title, self).__init__()
        super(Description, self).__init__()

        self.setTitleStr(strArg)
        self.setDescription()

        self.setPeriod(intArg)

        self.color = None
        self.child = []
        self.dateBegin = None
        self.dateEnd = None
        self.dateScheduled = None
        self.data = None

        self.setPlan()
        self.setPlot()


    def __str__(self):

        """  """

        strResult = '\n* ' + self.getTitleStr() + ' (' + str(len(self)) + ' ' + self.dateBegin.strftime("%Y-%m-%d") + ' .. ' + self.dateEnd.strftime("%Y-%m-%d") + ')' + '\n\n'

        strResult += self.__listDescriptionToString__()

        for c in self.child:
            strResult += str(c) + '\n'

        return strResult


    def __len__(self):

        """  """

        l = 0
        for c in self.child:
            if type(c) == Cycle or type(c) == Period:
                l += len(c)

        if self.periodInt == None or l > self.periodInt:
            self.setPeriod(l)

        return self.periodInt


    def setPlan(self,fPlan=True):

        """  """

        for c in self.child:
            if type(c) == Cycle or type(c) == Period:
                c.setPlan(fPlan)

        self.fPlan = fPlan

        return self


    def appendDescription(self,objArg):

        """  """

        if objArg != None and len(objArg) > 0:
            super().appendDescription(objArg)

        return self


    def resetDistances(self):

        """  """

        for c in self.child:
            if type(c) == Cycle or type(c) == Period:
                c.resetDistances()

        self.data = []

        return self


    def appendChildDescription(self,objArg):

        """  """

        if len(self.child) > 0:
            self.child[-1].appendDescription(objArg)


    def getDuration(self):

        """ return a timedelta """

        # TODO: use self.data

        intResult = 0
        if len(self.child) > 0:
            for u in self.child:
                if type(u) == Cycle or type(u) == Period:
                    intResult += u.getDuration().total_seconds()
        elif len(self.data) > 0:
            for t in map(lambda lst: lst[2], self.data):
                intResult += round(t * 60.0)

        return timedelta(seconds=intResult)


    def getNumberOfCycles(self):

        """  """

        # TODO: use self.data

        intResult = 0
        for c in self.child:
            if type(c) == Period:
                intResult += c.getNumberOfCycles()
            elif type(c) == Cycle:
                intResult += 1

        return intResult


    def getNumberOfUnits(self):

        """  """

        # TODO: use self.data

        intResult = 0
        for c in self.child:
            if type(c) == Cycle or type(c) == Period:
                intResult += c.getNumberOfUnits()

        return intResult


    def getDateString(self):

        """  """

        strResult = ''

        if type(self.dateBegin) == date and self.dateBegin != None and type(self.dateEnd) == date and self.dateEnd != None:
            strResult = ' (' + str(len(self)) + ' ' + self.dateBegin.strftime("%Y-%m-%d") + ' .. ' + self.dateEnd.strftime("%Y-%m-%d") + ')'

        return strResult


    def append(self,objArg):

        """  """

        # print(f'info: reset data collection of period "{self.getTitleStr()}"', file=sys.stderr)
        self.data = None

        if objArg == None:
            print('error: ' + str(objArg), file=sys.stderr)
        elif type(objArg) == list:
            for a in objArg:
                self.append(a)
        elif objArg == None or (type(objArg) != Cycle and type(objArg) != Period and type(objArg) != Note):
            print('error: ' + str(objArg), file=sys.stderr)
        else:
            self.child.append(objArg.dup())

        return self


    def insert(self,objArg):

        """  """

        objResult = self

        if objArg == None or objArg.dateBegin == None:
            print('error: date begin', file=sys.stderr)
        elif self.dateBegin == None:
            print('error: date begin', file=sys.stderr)
        elif type(objArg) == Cycle or type(objArg) == Period:
            p = self.getPeriodByDate(objArg.dateBegin)
            if p == None:
                print('error: no according period found' + str(objArg), file=sys.stderr)
            elif len(p.child) < 1:
                p.child.append(objArg.dup())
            else:
                i = 0
                for i in range(len(p.child)):
                    if type(p.child[i]) == Cycle or type(p.child[i]) == Period:
                        if p.child[i].dateBegin >= objArg.dateBegin:
                            p.child.insert(i,objArg.dup())
                            break
                        elif p.child[i] == p.child[-1]:
                            p.child.append(objArg.dup())
                    i += 1
                self.schedule()

        return objResult


    def insertByDate(self,objArg,flagReplace=False):

        """  """

        objResult = self

        if objArg == None:
            pass
        elif self.dateBegin == None:
            print('error: date begin', file=sys.stderr)
        elif type(objArg) == Cycle:
            d = 0
            for v in objArg.day:
                if len(v) < 1:
                    # day without elements
                    if flagReplace:
                        # create a scheduled empty unit to override
                        u = Unit()
                        u.setDate(objArg.dateBegin + timedelta(days=d))
                        self.insertByDate(u,True)
                else:
                    for u in v:
                        if type(u) == Unit or type(u) == Combination:
                            self.insertByDate(u,flagReplace)
                        else:
                            print('error: type ' + str(type(u)), file=sys.stderr)
                d += 1

            if flagReplace:
                c = self.getCycleByDate(objArg.dateBegin)
                if c != None:
                    if objArg.hasTitle():
                        # copy title from objArg to c
                        c.setTitleStr(objArg.getTitleStr())
                    if objArg.hasDescription():
                        # copy description from objArg to c
                        c.setDescription(objArg.getDescription())
                # TODO: handle multiple affected cycles
                # TODO: transfer color etc

        elif objArg != None and objArg.dt != None:
            if len(self.child) < 1:
                # there is no child cycle yet
                delta = objArg.dt.date() - self.dateBegin
                if delta.days > -1 and objArg.dt.date() <= self.dateEnd:
                    l = self.dateEnd - self.dateBegin
                    c = Cycle(self.getTitleStr(), l.days + 1)
                    c.schedule(self.dateBegin.year,self.dateBegin.month,self.dateBegin.day)
                    c.insertByDate(objArg,flagReplace)
                    self.append(c)
            else:
                for c in self.child:
                    if type(c) == Cycle or type(c) == Period:
                        c.insertByDate(objArg,flagReplace)

        return objResult


    def getCycleByDate(self,objDate=None):

        """  """

        if objDate == None:
            return self.getCycleByDate(datetime.now())
        elif type(objDate) == str:
            return self.getCycleByDate(datetime.fromisoformat(objDate))
        elif type(objDate) == date:
            return self.getCycleByDate(datetime.combine(objDate,time(0)))
        elif type(objDate) == datetime:
            for c in self.child:
                if type(c) == Period:
                    if c.dateBegin <= objDate.date() and objDate.date() <= c.dateEnd:
                        return c.getCycleByDate(objDate)
                elif type(c) == Cycle:
                    r = c.getCycleByDate(objDate)
                    if r != None:
                        return r

        return None


    def getPeriodByDate(self,objDate=None):

        """  """

        if objDate == None:
            return self.getPeriodByDate(datetime.now())
        elif type(objDate) == str:
            return self.getPeriodByDate(datetime.fromisoformat(objDate))
        elif type(objDate) == date:
            return self.getPeriodByDate(datetime.combine(objDate,time(0)))
        elif type(objDate) == datetime:
            if len(self.child) < 1:
                if self.dateBegin <= objDate.date() and objDate.date() <= self.dateEnd:
                    return self
            else:
                for c in self.child:
                    if type(c) == Period:
                        if c.dateBegin <= objDate.date() and objDate.date() <= c.dateEnd:
                            return c.getPeriodByDate(objDate)
                    elif type(c) == Cycle and c.getCycleByDate(objDate) != None:
                        return self
        else:
            print('error: no according period found' + str(objDate), file=sys.stderr)

        return None


    def setPeriod(self, intArg):

        """  """

        self.periodInt = intArg

        return self


    def scale(self,floatScale,patternType=None):

        """  """

        if len(self.child) > 0:
            for c in self.child:
                if type(c) == Cycle or type(c) == Period:
                    c.scale(floatScale,patternType)
        elif len(self.data) > 0:
            l = []
            for d in self.data:
                l.append([0,d[1]*floatScale,d[2]*floatScale,d[3]])
            self.data = l
            
        return self


    def swap(self,intA,intB):

        """  """

        # TODO: swap childs

        return self


    def remove(self,patternType=None):

        """  """

        for c in self.child:
            if type(c) == Cycle or type(c) == Period:
                c.remove(patternType=patternType)

        return self


    def schedule(self, intYear=None, intMonth=None, intDay=None):

        """  """

        if intYear == None and intMonth == None and intDay == None:
            if self.dateScheduled != None:
                # re-use former schedule date
                pass
            elif len(self.child) > 0:
                print('info: set dates of period according to childs', file=sys.stderr)
                self.dateBegin = self.child[0].dateBegin
                self.dateEnd = self.child[-1].dateEnd
                return self
            else:
                print('error: cannot set dates according to childs', file=sys.stderr)
                return None
        else:

            try:
                if intMonth == None and intDay == None:
                    self.dateScheduled = date(intYear, 1, 1)
                elif intDay == None:
                    self.dateScheduled = date(intYear, intMonth, 1)
                else:
                    self.dateScheduled = date(intYear, intMonth, intDay)
            except ValueError as e:
                print('error: ' + str(e), file=sys.stderr)
                return None

        e = self.dateScheduled
        for c in self.child:
            if type(c) == Cycle or type(c) == Period:
                c.schedule(e.year, e.month, e.day)
                e += timedelta(days=len(c))
            elif type(c) == Note:
                c.dt = e
                #print('type: ' + c.dt.isoformat(), file=sys.stderr)

        self.dateBegin = self.dateScheduled
        self.dateEnd = self.dateBegin + timedelta(days=(len(self) - 1))

        return self


    def define(self, objArg=None):

        """  """

        if self.data != None and len(self.data) > 0:
            print(f'error: cannot override existing data collection of period "{self.getTitleStr()}"', file=sys.stderr)
        elif objArg == None:
            print('error: empty period initialization', file=sys.stderr)
        elif type(objArg) == str and len(objArg) > 0:
            return self.define([objArg])
        elif type(objArg) == list and len(objArg) > 0:
            self.data = []
            u = Unit()
            for s in objArg:
                #print('info: ' + s, file=sys.stderr)
                if u.parse(s):
                    #print('info: ' + str(u.stat()), file=sys.stderr)
                    self.data.extend(u.stat())
                else:
                    print('error: parsing ' + s, file=sys.stderr)
            print('info: ' + str(list(map(lambda lst: lst[2], self.data))), file=sys.stderr)
        else:
            print('error: empty period initialization', file=sys.stderr)
            
        return self


    def stat(self):

        """  """

        listResult = []

        if type(self.data) == list and len(self.data) > 0:
            listResult = self.data
        else:
            for c in self.child:
                if type(c) == Cycle or type(c) == Period:
                    listResult.extend(c.stat())
            self.data = listResult

        return listResult


    def report(self, dictArg=None):

        """  """

        strResult = ''

        self.stat()

        l = np.array(list(map(lambda lst: lst[2], self.data)))
        sum_h = l.sum() / 60

        if dictArg == None:
            dictArg = {}

        for u in self.data:

            if u[3] not in dictArg:
                dictArg[u[3]] = [[],[]]

            dictArg[u[3]][0].append(u[1])
            dictArg[u[3]][1].append(u[2])

        for k in sorted(set(map(lambda lst: lst[3], self.data))):
            # all kinds of units
            sum_k = sum(dictArg[k][1]) / 60.0

            if sum_h < 0.01:
                pass
            elif len(dictArg[k][0]) < 1:
                strResult += ("{:4} x {:" + str(config.max_length_type) + "} {:7}    {:7.01f} h {:.02f}\n").format(len(dictArg[k][0]),
                                                                                                                   k,
                                                                                                                   ' ',
                                                                                                                   round(sum_k, 1),
                                                                                                                   round(sum_k / sum_h, 2))
            elif len(dictArg[k][0]) < 3:
                strResult += ("{:4} x {:" + str(config.max_length_type) + "} {:7.01f} {} {:7.01f} h {:.02f}\n").format(len(dictArg[k][0]), k, sum(dictArg[k][0]),
                                                                                                                       config.unit_distance,
                                                                                                                       round(sum_k,1),
                                                                                                                       round(sum_k / sum_h, 2))
            else:
                strResult += ("{:4} x {:" + str(config.max_length_type) + "} {:7.01f} {} {:7.01f} h {:.02f} {:5.01f} /{:5.01f} /{:5.01f}\n").format(len(dictArg[k][0]),
                                                                                                                                                    k,
                                                                                                                                                    sum(dictArg[k][0]),
                                                                                                                                                    config.unit_distance,
                                                                                                                                                    round(sum_k, 2),
                                                                                                                                                    round(sum_k / sum_h, 2),
                                                                                                                                                    min(dictArg[k][0]),
                                                                                                                                                    mean(dictArg[k][0]),
                                                                                                                                                    max(dictArg[k][0]))

        n = self.getNumberOfUnits()
        if True or n > 0 or (len(self.data) > 0 and len(self.child) < 1):
            p = len(self)
            strResult += "\n{} Units {:.2f} h in {} Days ≌ {:.2f} h/Week ≌ {:.0f} min/d\n".format(n, round(sum_h,2), p, sum_h * 7.0 / p, sum_h * 60 / p)

        return strResult


    def parseFile(self,listFilename,fUpdater=None):

        """  """

        if type(listFilename) == str:
            listFilename = [listFilename]

        self.setPlan(False)
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
                if l == None or l == '' or re.match(r"^sep",l) or re.match(r"^\*",l):
                    pass
                elif (fUpdater != None and t.parse(fUpdater(l))) or t.parse(l):
                    if t.dt != None:
                        d_i = t.dt
                        if d0 == None or t.dt < d0:
                            d0 = t.dt
                        if d1 == None or t.dt > d1:
                            d1 = t.dt
                    else:
                        t.dt = d_i

                    a.append(t)
                    t = Unit()
                elif (fUpdater != None and n.parse(fUpdater(l))) or n.parse(l):
                    if n.dt != None:
                        d_i = n.dt
                        if d0 == None or n.dt < d0:
                            d0 = t.dt
                        if d1 == None or n.dt > d1:
                            d1 = t.dt
                    else:
                        n.dt = d_i

                    a.append(n)
                    n = Note()
                else:
                    print('error: ' + l, file=sys.stderr)

        if d0 == None:
            print('No Report possible', file=sys.stderr)
        else:
            print('Report {} .. {}'.format(d0.strftime("%Y-%m-%d"),d1.strftime("%Y-%m-%d")), file=sys.stderr)

            delta = d1 - d0

            if len(self.child) > 0:
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
                self.insertByDate(t)

        return self


    def dup(self):

        """  """

        return copy.deepcopy(self)


    def toString(self):

        """  """

        return str(self)


    def toHtmlTable(self):

        """  """

        return self.toHtml()


    def toHtml(self):

        """  """

        strResult = '<section class="{}" id="{}"'.format(__name__, str(id(self)))

        if self.color != None:
            strResult += ' style="background-color: {}"'.format(self.color)

        strResult += '><div class="header">' + self.getTitleXML()
        if self.dateBegin != None and self.dateEnd != None:
            strResult += self.getDateString()
        strResult += '</div>\n'

        strResult += '<ul>' + self.__listDescriptionToHtml__() + '</ul>'

        strResult += '<pre>' + self.report() + '</pre>'

        if self.getNumberOfCycles() > 0 and self.fPlot:
            strResult += '<div>'
            strResult += self.plotAccumulationDuration()
            strResult += self.plotAccumulation()
            strResult += self.plotHist()
            strResult += self.plotTimeDist()
            #strResult += self.toSVGGanttChart()
            #strResult += self.toSVGDiagram()
            strResult += '</div>'

        for c in self.child:
            strResult += c.toHtmlTable() + '\n'
            #strResult += c.toHtml() + '\n'

        strResult += '</section>\n'

        return strResult


    def toHtmlTableOfContent(self,strIndent=''):

        """  """

        strResult = self.getTitleLineTableOfContent(strIndent) + self.getDateString() + '\n'

        for c in self.child:
            if type(c) == Period:
                strResult += c.toHtmlTableOfContent(strIndent + '    ')
            elif type(c) == Cycle:
                strResult += c.getTitleLineTableOfContent(strIndent + '    ') + '\n'

        return strResult


    def toHtmlFile(self):

        """ returns html/body + content """

        strResult = '<!doctype html public "-//IETF//DTD HTML 4.0//EN">'

        strResult += "<html>"

        strResult += "<head>"

        strResult += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>'

        strResult += "<title></title>"

        strResult += "<style>\nbody {font-family: Arial,sans-serif; font-size:12px; margin: 5px 5px 5px 5px;}\nsvg {margin: 5px 0;}\nsection {border-left: 1px dotted #aaaaaa;}\nsection > * {margin: 0px 0px 0px 2px;}\nsection > *:not(.header) {margin: 0.5em 0.5em 0.5em 2em;}\ndiv.header {font-weight:bold;}\nul, ol {padding: 0px 0px 0px 2em;}\npre {background-color: #f8f8f8;border: 1px solid #cccccc;padding: 6px 3px;border-radius: 3px;}\na:link {text-decoration:none;}\ntable {width: 95%; border-collapse: collapse; empty-cells:show; margin-left:auto; margin-right:auto; border: 1px solid grey;}\ntd { border: 1px solid grey; vertical-align:top;}\n.empty {margin-bottom:0px;}\n</style>\n"

        strResult += "</head>\n<body>\n"

        strResult += '<pre>' + self.toHtmlTableOfContent() + '</pre>\n'

        strResult += '<div style="text-align: center;margin: 40px;">' + self.toSVGGanttChart() + '</div>\n'

        strResult += self.toHtml()

        strResult += "</body>\n</html>"

        return strResult


    def toComparisonHtmlFile(self, listArg=[]):

        """ returns html/body + content """

        strResult = '<!doctype html public "-//IETF//DTD HTML 4.0//EN">'

        strResult += "<html>"

        strResult += "<head>"

        strResult += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>'

        strResult += "<title></title>"

        strResult += "<style>\nbody {font-family: Arial,sans-serif; font-size:12px; margin: 5px 5px 5px 5px;}\nsvg {margin: 5px 0;}\nsection {border-left: 1px dotted #aaaaaa;}\nsection > * {margin: 0px 0px 0px 2px;}\nsection > *:not(.header) {margin: 0.5em 0.5em 0.5em 2em;}\ndiv.header {font-weight:bold;}\nul, ol {padding: 0px 0px 0px 2em;}\npre {background-color: #f8f8f8;border: 1px solid #cccccc;padding: 6px 3px;border-radius: 3px;}\na:link {text-decoration:none;}\ntable {width: 95%; border-collapse: collapse; empty-cells:show; margin-left:auto; margin-right:auto; border: 1px solid grey;}\ntd { border: 1px solid grey; vertical-align:top;}\n.empty {margin-bottom:0px;}\n</style>\n"

        strResult += "</head>\n<body>\n"

        if len(listArg) < 1:
            l = self.child
        else:
            l = listArg

        for c in l:
            if type(c) == Period or type(c) == Cycle:
                strResult += '<section class="{}" id="{}">'.format(__name__, str(id(c)))

                strResult += '<div class="header">' + c.getTitleXML()
                if c.dateBegin != None and c.dateEnd != None:
                    strResult += c.getDateString()
                strResult += '</div>\n'

                strResult += '<pre>' + c.report() + '</pre>'

                if self.getNumberOfCycles() > 0 and self.fPlot:
                    strResult += '<div>'
                    strResult += c.plotAccumulationDuration()
                    strResult += c.plotAccumulation()
                    strResult += c.plotHist()
                    strResult += c.plotTimeDist()
                    #strResult += c.toSVGGanttChart()
                    #strResult += c.toSVGDiagram()
                    strResult += '</div>'

                strResult += '</section>\n'

        strResult += "</body>\n</html>"

        return strResult


    def toCSV(self):

        """  """

        strResult = '\n* ' + self.getTitleStr()
        if self.dateBegin != None and self.dateEnd != None:
            strResult += self.getDateString()
        strResult += '\n'

        for c in self.child:
            strResult += c.toCSV() + '\n'

        return strResult


    def toFreemindNode(self):

        """  """

        strResult = '<node'
        if self.color != None:
           strResult += ' BACKGROUND_COLOR="{}"'.format(self.color)
        elif self.getNumberOfUnits() < 1:
           strResult += ' BACKGROUND_COLOR="{}"'.format('#ffaaaa')
        else:
            strResult += ' FOLDED="{}"'.format('false')

        strResult += ' TEXT="' + self.getTitleXML()
        if self.dateBegin != None and self.dateEnd != None:
            strResult += '&#xa; ' + self.getDateString() + '&#xa;' + self.report().replace('\n','&#xa;')
        strResult += '">\n'

        strResult += '<font BOLD="true" NAME="Monospaced" SIZE="12"/>'

        strResult += self.__listDescriptionToFreemind__()

        for c in self.child:
            strResult += c.toFreemindNode()

        strResult += '</node>\n'

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
        for c in self.child:
            if type(c) == Cycle or type(c) == Period:
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


    def toSVG(self, x = config.diagram_offset, y=20):

        """  """

        strResult = '<g>'

        if self.color != None and len(self) > 0:
            strResult += '<rect fill="{}" x="{}" y="{}" height="{}" width="{}"/>\n'.format(self.color,1,y+1,((config.diagram_bar_height * 2)*len(self))-2,x+config.diagram_width-4)

        if len(self.child) < 1:
            strResult += '<text x="{}" y="{}" style="vertical-align:top"><tspan x="10" dy="1.5em">{}</tspan><tspan x="10" dy="1.5em">{}</tspan></text>\n'.format(0,y,self.getTitleXML(), self.getDateString())
            strResult += '<line stroke="black" stroke-width=".5" stroke-dasharray="2,10" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(0,y,x+config.diagram_width,y)
            for d in range(0,len(self)):
                strResult += '<line stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(x,y,x,y+config.diagram_bar_height)
                y += config.diagram_bar_height * 2
        else:
            for c in self.child:
                if type(c) == Cycle or type(c) == Period:
                    #strResult += '<line stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(x,y,x+400,y)
                    #strResult += '<text x="{}" y="{}">{}</text>\n'.format(x+400,y,c.getTitleXML())
                    strResult += c.toSVG(x,y)
                    y += len(c) * config.diagram_bar_height * 2

        strResult += '</g>'

        return strResult


    def toSVGDiagram(self):

        """  """

        diagram_height = len(self) * (config.diagram_bar_height * 2) + 100
        strResult = '<svg baseProfile="full" height="{}" version="1.1" width="{}" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink">'.format(diagram_height, config.diagram_width)

        strResult += '<style type="text/css">svg { font-family: ' + config.font_family + '; font-size: ' + str(config.font_size) + 'pt; }</style>'

        #strResult += '<g transform="rotate(90)">'
        #'<text x="210" y="110">Period 2.2021</text>

        for i in [3600/4,3600/2,3600,2*3600,3*3600,4*3600,5*3600,6*3600]:
            w = i / 3600 * 25 * config.diagram_scale_dist
            strResult += '<line stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format( config.diagram_offset + w, 20, config.diagram_offset + w, diagram_height)

        strResult += self.toSVG()
        #strResult += '</g>'
        strResult += '</svg>\n'

        return strResult


    def toSVGGantt(self,dateBase,y=0):

        """  """

        try:
            l = self.dateEnd - self.dateBegin
            x_i = (self.dateBegin - dateBase).days * 2
        except TypeError:
            return '<text x="{}" y="{}">{}</text>\n'.format(0 + 2, y + 10,self.getTitleXML())

        strResult = '<g>'

        if self.color == None:
            c = '#aaaaff'
        else:
            c = self.color

        strResult += '<rect fill="{}" opacity=".75" x="{}" y="{}" height="{}" width="{}" rx="2">\n'.format(c, x_i, y, config.diagram_bar_height*2, (l.days + 1) * 2)
        strResult += '<title>{}</title>\n'.format(self.getTitleXML() + self.getDateString() + '\n\n' + self.__listDescriptionToSVG__() + '\n\n' + self.report())
        strResult += '</rect>'
        strResult += '<text x="{}" y="{}">{}</text>\n'.format(x_i + 2, y + 10,self.getTitleXML())

        y_i = y + config.diagram_bar_height * 3
        for c in self.child:
            if type(c) == Cycle or type(c) == Period:
                strResult += c.toSVGGanttBar(dateBase,y_i)
                if type(c) == Period:
                    strResult += c.toSVGGantt(dateBase,y_i)
                y_i += config.diagram_bar_height * 3
                
        strResult += '<line stroke-dasharray="4" stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(x_i + (l.days + 1) * 2, y, x_i + (l.days + 1) * 2, y_i)

        strResult += '</g>'

        return strResult


    def toSVGGanttChart(self):

        """ Gantt chart of periods and cycles """

        d_0 = None
        d_1 = None
        for c in self.child:
            if type(c) == Cycle or type(c) == Period:
                if d_0 == None:
                    d_0 = c.dateBegin
                if d_1 == None:
                    d_1 = self.child[-1].dateEnd

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

            strResult += '<line stroke-dasharray="8" stroke="{}" stroke-width="1" opacity="0.25" x1="{}" y1="{}" x2="{}" y2="{}">\n'.format(color,w, 0, w, diagram_height)
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

        strResult += self.toSVGGantt(d_0)
        strResult += '</g>'
        strResult += '</svg>\n'

        return strResult


    def to_ical(self,cal):

        """  """

        for c in self.child:
            c.to_ical(cal)


    def toVCalendar(self):

        """  """

        cal = Calendar()
        cal.add('prodid', '-//{title}//  //'.format(title=self.getTitleStr()))
        cal.add('version', '2.0')
        self.to_ical(cal)
        return cal.to_ical()


    def CalendarYearPeriod(self,intYear,strArg=None):

        """ returns a plain calendar year period """

        try:
            date(intYear, 2, 29)
            self.append(Cycle(str(intYear),366))
        except ValueError:
            self.append(Cycle(str(intYear),365))

        if strArg != None and len(strArg) > 0:
            self.setTitleStr(strArg)

        self.schedule(intYear,1,1)

        return self


    def CalendarSeasonPeriod(self,intYear,strArg=None):

        """ returns a plain calendar year containing seasons periods """

        # begin of year
        d_0 = date(intYear,1,1)

        s = 'Winter {}'.format(intYear)
        # begin of spring
        d_1 = date(intYear,3,21)
        self.append(Period(s).append(Cycle(s, round((d_1 - d_0).total_seconds() / (24 * 60 * 60)))))

        s = 'Spring {}'.format(intYear)
        # begin of summer
        d_2 = date(intYear,6,21)
        self.append(Period(s).append(Cycle(s, round((d_2 - d_1).total_seconds() / (24 * 60 * 60)))))

        # begin of autumn
        s = 'Summer {}'.format(intYear)
        d_3 = date(intYear,9,21)
        self.append(Period(s).append(Cycle(s, round((d_3 - d_2).total_seconds() / (24 * 60 * 60)))))

        s = 'Autumn {}'.format(intYear)
        # begin of winter
        d_4 = date(intYear,12,21)
        self.append(Period(s).append(Cycle(s, round((d_4 - d_3).total_seconds() / (24 * 60 * 60)))))

        s = 'Winter ' + str(intYear+1)
        # begin of next year
        d_5 = date(intYear+1,1,1)
        self.append(Period(s).append(Cycle(s, round((d_5 - d_4).total_seconds() / (24 * 60 * 60)))))

        if strArg != None and len(strArg) > 0:
            self.setTitleStr(strArg)

        self.schedule(intYear,1,1)

        return self


    def CalendarWeekPeriod(self,intYear,strArg=None):

        """ fills a period calendar year containing week periods """

        for w in range(1,54):
            self.append(Cycle('CW{}/{}'.format(w, intYear), 7))

        d = date(intYear,1,1)
        if d.isoweekday() > 4:
            # skip to next monday
            d += timedelta(days=(8 - d.isoweekday()))
        else:
            # skip to previous monday
            d -= timedelta(days=(d.isoweekday() - 1))

        if strArg != None and len(strArg) > 0:
            self.setTitleStr(strArg)

        self.schedule(d.year,d.month,d.day)

        return self


    def CalendarMonthPeriod(self,intYear,strArg=None):

        """ returns a calendar year containing month periods """

        for m in range(1,13):
            if m > 11:
                d = date(intYear+1,1,1) - date(intYear,m,1)
            else:
                d = date(intYear,m+1,1) - date(intYear,m,1)

            self.append(Cycle('{}.{}'.format(intYear,m), d.days))

        if strArg != None and len(strArg) > 0:
            self.setTitleStr(strArg)

        self.schedule(intYear,1,1)

        return self


    def CalendarLastWeeksPeriod(self,intWeek=26,strArg=None):

        """ returns a last weeks as periods """

        dt_0 = datetime.now()
        dt_i = dt_0 + timedelta(days=(7 - dt_0.weekday())) - timedelta(weeks=intWeek)
        dt_1 = dt_i

        for m in range(0,intWeek):
            self.append(Cycle(dt_i.strftime("%Y-W%U")))
            dt_i += timedelta(weeks=1)

        if strArg != None and len(strArg) > 0:
            self.setTitleStr(strArg)

        self.schedule(dt_1.year,dt_1.month,dt_1.day)

        return self


    def CalendarLastMonthsPeriod(self,intMonth=6,strArg=None):

        """ returns a last months (= 4 weeks) as periods """

        dt_0 = datetime.now()
        dt_i = dt_0 + timedelta(days=(7 - dt_0.weekday())) - timedelta(weeks = intMonth * 4)
        dt_1 = dt_i

        for m in range(0,intMonth):
            self.append(Cycle(dt_i.strftime("%Y-M%m"),4*7))
            dt_i += timedelta(weeks=4)

        if strArg != None and len(strArg) > 0:
            self.setTitleStr(strArg)

        self.schedule(dt_1.year,dt_1.month,dt_1.day)

        return self
