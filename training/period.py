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
        super(Plot, self).__init__()

        self.setTitleStr(strArg)
        self.setDescription()

        self.setPeriod(intArg)

        self.color = None
        self.child = []
        self.data = []
        self.summary = {}

        self.dateBegin = None
        self.dateEnd = None
        self.dateFixed = None

        self.setPlan()
        self.setPlot()
        self.setTextOnly(False)
        self.setVDefaults()


    def __str__(self):

        """  """

        strResult = '\n* ' + super().getTitleString() + ' ' + super().getDateString() + '\n\n'

        strResult += self.getDescriptionString()

        strResult += self.report()

        for c in self.child:
            strResult += str(c) + '\n'

        return strResult


    def __len__(self):

        """  """

        l = 0
        for c in self.child:
            if type(c) is Cycle or type(c) is Period:
                l += c.getLength()

        if self.periodInt is None or l > self.periodInt:
            self.setPeriod(l)

        return self.periodInt


    def setPlan(self,fPlan=True):

        """  """

        for c in self.child:
            if type(c) is Cycle or type(c) is Period:
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


    def updateValues(self,dictArg=None):

        """  """

        # TODO: if not dictArg: derive values from other units

        if dictArg is not None:
            self.setVDefaults(dictArg)

        if self.child:
            for c in self.child:
                if type(c) is Cycle or type(c) is Period:
                    c.updateValues(self.v_defaults)
        elif self.data:
            for d in self.data:
                # see Unit.updateValues() but d is not an Unit() !
                    
                # TODO: use dictArg.keys() with config.max_length_type
                if d[3] is None:
                    pass
                else:
                    k = d[3][0:config.max_length_type]
                    if k in self.v_defaults and self.v_defaults[k] > 1.0 and d[2] is not None and d[2] > 0.0:
                        if d[1] is None or d[1] < 0.1:
                            # there is a defined default velocity
                            d[1] = self.v_defaults[k] * (d[2] / 3600)
                    elif k in self.v_defaults and self.v_defaults[k] > 1.0 and d[1] is not None and d[1] > 0.1:
                        if d[2] is None or d[2] < 1.0:
                            # there is a defined default velocity
                            d[2] = int(d[1] / self.v_defaults[k] * 60)

        return self


    def resetDistances(self):

        """  """

        for c in self.child:
            if type(c) is Cycle or type(c) is Period:
                c.resetDistances()

        self.data.clear()
        #super(Plot, self).__init__()
        #self.strPlotAccumulation = None
        Plot.__init__(self)

        return self


    def resetDescription(self):

        """  """

        self.setDescription(None)

        for c in self.child:
            if type(c) is Cycle or type(c) is Period:
                c.resetDescription()

        return self


    def appendChildDescription(self,objArg):

        """  """

        if self.child:
            self.child[-1].appendDescription(objArg)


    def getLength(self):

        """ return length of period """

        return len(self)


    def getDuration(self):

        """ return a timedelta """

        # TODO: use self.data

        intResult = 0
        if self.child:
            for u in self.child:
                if type(u) is Cycle or type(u) is Period:
                    intResult += u.getDuration().total_seconds()
        elif self.data:
            for t in map(lambda lst: lst[2], self.data):
                intResult += round(t * 60.0)

        return timedelta(seconds=intResult)


    def getNumberOfCycles(self):

        """  """

        # TODO: use self.data

        intResult = 0
        for c in self.child:
            if type(c) is Period:
                intResult += c.getNumberOfCycles()
            elif type(c) is Cycle:
                intResult += 1

        return intResult


    def getNumberOfUnits(self):

        """  """

        # TODO: use self.data

        intResult = 0
        for c in self.child:
            if type(c) is Cycle or type(c) is Period:
                intResult += c.getNumberOfUnits()

        return intResult


    def append(self,objArg):

        """  """

        # print(f'info: reset data collection of period "{self.getTitleStr()}"', file=sys.stderr)
        self.data.clear()
        self.summary.clear()

        if objArg is None:
            print('error: ' + str(objArg), file=sys.stderr)
        elif type(objArg) is list:
            for a in objArg:
                self.append(a)
        elif objArg is None or (type(objArg) != Cycle and type(objArg) != Period and type(objArg) != Note):
            print('error: ' + str(objArg), file=sys.stderr)
        else:
            self.child.append(objArg.dup())
            self.schedule()

        return self


    def insert(self,objArg,intLevel=-1):

        """  """

        objResult = self

        if objArg is None:
            print('error: object', file=sys.stderr)
        elif self.dateBegin is None:
            print('error: date begin', file=sys.stderr)
        elif type(objArg) is Cycle or type(objArg) is Period:
            if objArg.dateBegin is None:
                print('error: date begin', file=sys.stderr)
            else:
                p = self.getPeriodByDate(objArg.dateBegin,intLevel)
                if p is None:
                    print('error: no according period found' + str(objArg), file=sys.stderr)
                elif not p.child:
                    p.child.append(objArg.dup())
                else:
                    i = 0
                    for i in range(len(p.child)):
                        if type(p.child[i]) is Cycle or type(p.child[i]) is Period:
                            if p.child[i].dateBegin == objArg.dateBegin:
                                # begin is equal
                                p.child.insert(i,objArg.dup())
                                break
                            elif p.child[i].dateEnd >= objArg.dateBegin:
                                # objArg begins in p.child[i]
                                p.child[i].cut(objArg.dateBegin)
                                p.child.insert(i+1,objArg.dup())
                                break
                            elif p.child[i] == p.child[-1]:
                                print('error: no cycle found', file=sys.stderr)
                                p.child.append(objArg.dup())
                        i += 1
                self.schedule()
        elif type(objArg) is Note or type(objArg) is Unit or type(objArg) is Combination:
            if objArg.dt is None:
                print('error: date', file=sys.stderr)
            else:
                c = self.getCycleByDate(objArg.dt)
                if c is None or not c.day:
                    print('error: no cycle found', file=sys.stderr)
                else:
                    # is inside this Cycle
                    j = round((objArg.dt.date() - c.dateBegin).total_seconds() / (24 * 60 * 60))
                    c.insert(j,objArg.dup())
                self.schedule()

        return objResult


    def insertByDate(self,objArg,flagReplace=False):

        """  """

        objResult = self

        if objArg is None:
            pass
        elif self.dateBegin is None:
            print('error: date begin', file=sys.stderr)
        elif type(objArg) is Cycle:
            d = 0
            for v in objArg.day:
                if not v:
                    # day without elements
                    if flagReplace:
                        # create a scheduled empty unit to override
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
                    c.insertByDate(objArg,flagReplace)
                    self.append(c)
            else:
                for c in self.child:
                    if type(c) is Cycle or type(c) is Period:
                        c.insertByDate(objArg,flagReplace)

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


    def setPeriod(self, intArg):

        """  """

        if intArg is None:
            self.periodInt = 0
        else:
            self.periodInt = intArg

        return self


    def scale(self,floatScale,patternType=None):

        """  """

        if self.child:
            for c in self.child:
                if type(c) is Cycle or type(c) is Period:
                    c.scale(floatScale,patternType)
        elif self.data:
            l = []
            for d in self.data:
                l.append([0,d[1]*floatScale,d[2]*floatScale,d[3]])
            self.data = l

        self.summary.clear()

        return self


    def swap(self,intA,intB):

        """  """

        # TODO: swap childs

        return self


    def remove(self,patternType=None):

        """  """

        if self.child:
            for c in self.child:
                if type(c) is Cycle or type(c) is Period:
                    c.remove(patternType=patternType)
        elif self.data:
            l = []
            for d in self.data:
                if re.match(patternType,d[3]):
                    pass
                else:
                    l.append(d)
            self.data = l

        self.summary.clear()

        return self


    def cut(self,objArg=0):

        """  """

        #print('info: cut "' + self.getTitleString() + '" at ' + str(objArg), file=sys.stderr)
        if type(objArg) is date:
            #
            if objArg <= self.dateEnd:
                d = (objArg - self.dateBegin).days
                if d > 0:
                    self.cut(d)
                else:
                    print('info: ' + objArg.isoformat() + ' is not in this period', file=sys.stderr)
        elif type(objArg) is int and objArg > 0 and not self.child:
            # a period without childs
            self.setPeriod(objArg)
            self.schedule()
        elif type(objArg) is int and objArg > 0 and self.getLength() > objArg:
            l = 0
            for i in range(len(self.child)):
                if type(self.child[i]) is Cycle or type(self.child[i]) is Period:
                    if l + self.child[i].getLength() == objArg:
                        #print('info: keep "' + self.child[i].getTitleString() + '" at ' + str(self.child[i].getLength()), file=sys.stderr)
                        del self.child[i+1:]
                        break
                    elif l + self.child[i].getLength() > objArg:
                        #print('info: cut "' + self.child[i].getTitleString() + '" at ' + str(objArg - l), file=sys.stderr)
                        del self.child[i+1:]
                        self.child[i].cut(objArg - l)
                        break
                    else:
                        #print('info: keep "' + self.child[i].getTitleString() + '" length ' + str(self.child[i].getLength()), file=sys.stderr)
                        l += self.child[i].getLength()

            self.setPeriod(objArg)
            self.schedule()
        else:
            print('error: wrong argument type ' + str(type(objArg)), file=sys.stderr)

        self.data.clear()
        self.summary.clear()

        return self


    def schedule(self, argDateOrYear=None, intMonth=None, intDay=None):

        """  """

        if self.dateFixed is not None:
            # keep fixed date and schedule childs
            self.dateBegin = self.dateFixed
        elif type(argDateOrYear) is date:
            self.dateBegin = argDateOrYear
        elif argDateOrYear is not None and type(argDateOrYear) is int and argDateOrYear > 1970 and argDateOrYear < 2100:
            if intMonth is None and intDay is None:
                self.dateBegin = date(argDateOrYear, 1, 1)
            elif intMonth is not None and intMonth > 0 and intMonth < 13:
                if intDay is None:
                    self.dateBegin = date(argDateOrYear, intMonth, 1)
                elif intDay > 0 and intDay < 32:
                    try:
                        # if mismatch intMonth and intDay
                        self.dateBegin = date(argDateOrYear, intMonth, intDay)
                    except ValueError as e:
                        print('error: ' + str(e), file=sys.stderr)
                        self.dateBegin = None
                else:
                    self.dateBegin = None

        dt_i = self.dateBegin

        if self.periodInt > 0 and self.dateBegin is not None:
            self.dateEnd = self.dateBegin + timedelta(days = self.periodInt - 1)

        if dt_i is not None and self.child:
            for c in self.child:
                if type(c) is Cycle or type(c) is Period:
                    c.schedule(dt_i)
                    if self.dateEnd is None or c.dateEnd > self.dateEnd:
                        self.dateEnd = c.dateEnd
                    dt_i = c.dateEnd + timedelta(days=1)
                elif type(c) is Note:
                    c.dt = dt_i

        return self


    def fix(self, objArg):

        """  """

        if self.dateFixed is not None:
            # keep fixed date
            pass
        elif objArg is not None and type(objArg) is date:
            self.dateFixed = objArg

        self.schedule()

        return self


    def define(self, objArg=None):

        """  """

        self.data.clear()
        self.summary.clear()

        if self.data is not None and self.data:
            print(f'error: cannot override existing data collection of period "{self.getTitleString()}"', file=sys.stderr)
        elif objArg is None:
            print('error: empty period initialization', file=sys.stderr)
        elif type(objArg) is str and objArg:
            return self.define([objArg])
        elif type(objArg) is list and objArg:
            u = Unit()
            for s in objArg:
                #print('info: ' + s, file=sys.stderr)
                if u.parse(s):
                    #print('info: ' + str(u.stat()), file=sys.stderr)
                    u.updateValues(self.v_defaults)
                    self.data.extend(u.stat())
                else:
                    print('error: parsing ' + s, file=sys.stderr)
            print('info: ' + str(list(map(lambda lst: lst[2], self.data))), file=sys.stderr)
        else:
            print('error: empty period initialization', file=sys.stderr)

        return self


    def stat(self):

        """ stat all descendant data to self.data and returns it as a nested list  """

        if self.child:
            self.data.clear()
            self.summary.clear()
            for c in self.child:
                if type(c) is Cycle or type(c) is Period:
                    self.data.extend(c.stat())

        return self.data


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


    def report(self):

        """  """

        strResult = ''

        n = self.getNumberOfUnits()
        if not self.data and n > 0:
            self.stat()

        sum_h = self.sum() / 60
        if sum_h < 0.1:
            return strResult

        for k in sorted(self.summary.keys()):
            # all kinds of units
            sum_k = sum(self.summary[k][1]) / 60.0

            if sum_h > 0.01:
                if n > 0:
                    strResult += f'{len(self.summary[k][0]):4} x '
                else:
                    strResult += '      '

                if not self.summary[k][0]:
                    strResult += ("{:" + str(config.max_length_type) + "} {:7}    {:7.01f} h {:.02f}\n").format(k,
                                                                                                                ' ',
                                                                                                                round(sum_k, 1),
                                                                                                                round(sum_k / sum_h, 2))
                elif len(self.summary[k][0]) < 3:
                    strResult += ("{:" + str(config.max_length_type) + "} {:7.01f} {} {:7.01f} h {:.02f}\n").format(k, 
                                                                                                                       sum(self.summary[k][0]),
                                                                                                                       config.unit_distance,
                                                                                                                       round(sum_k,1),
                                                                                                                       round(sum_k / sum_h, 2))
                else:
                    strResult += ("{:" + str(config.max_length_type) + "} {:7.01f} {} {:7.01f} h {:.02f} {:5.01f} /{:5.01f} /{:5.01f}\n").format(k,
                                                                                                                                                sum(self.summary[k][0]),
                                                                                                                                                config.unit_distance,
                                                                                                                                                round(sum_k, 2),
                                                                                                                                                round(sum_k / sum_h, 2),
                                                                                                                                                min(self.summary[k][0]),
                                                                                                                                                mean(self.summary[k][0]),
                                                                                                                                                max(self.summary[k][0]))

        if n > 0:
            strResult += f'\n{n} Units '
        else:
            strResult += '\n      '

        p = self.getLength()

        strResult += "{:.1f} h in {} Days ≌ {:.2f} h/Week ≌ {:.0f} min/d\n".format(round(sum_h,2), p, sum_h * 7.0 / p, sum_h * 60 / p)

        return strResult


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

            if self.child:
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

        self.setPlan(False)
        return self


    def dup(self):

        """  """

        return copy.deepcopy(self)


    def toString(self):

        """  """

        return str(self)


    def toTemplate(self):

        """ format this period and it's descendant periods to Python code for a high-level Plan Template """

        strResult = f'p = Period("{self.getTitleString()}").define({str(self.data)})\n'

        return strResult

        for c in self.child:
            if type(c) is Period:
                strResult += c.toTemplate()

        return strResult


    def toHtmlTable(self):

        """  """

        return self.toHtml()


    def toHtml(self):

        """  """

        strResult = '<section class="{}" id="{}"'.format(__name__, str(id(self)))

        if self.color is not None:
            strResult += ' style="background-color: {}"'.format(self.color)

        strResult += '><div class="header">' + self.getTitleXML()
        if self.dateBegin is not None and self.dateEnd is not None:
            strResult += self.getDateString()
        strResult += '</div>\n'

        strResult += self.getDescriptionHTML()

        if self.getNumberOfUnits() > 0 or self.data:
            strResult += '<pre style="width: 80%;">' + self.report() + '</pre>'

        if self.getNumberOfCycles() > 0 and self.fPlot:
            strResult += '<div style="text-align: center;margin: 0px;">'
            strResult += self.plotAccumulationDuration()
            strResult += self.plotAccumulation()
            strResult += self.plotHist()
            strResult += self.plotTimeDist()
            #strResult += self.toSVGGanttChart()
            #strResult += self.toSVGDiagram()
            strResult += '</div>'

        for c in self.child:
            strResult += c.toHtmlTable() + '\n'

        strResult += '</section>\n'

        return strResult


    def toHtmlTableOfContent(self,strIndent=''):

        """  """

        strResult = self.getTitleLineTableOfContent(strIndent) + self.getDateString() + '\n'

        for c in self.child:
            if type(c) is Period:
                strResult += c.toHtmlTableOfContent(strIndent + '    ')
            elif type(c) is Cycle:
                strResult += c.getTitleLineTableOfContent(strIndent + '    ') + '\n'

        return strResult


    def toHtmlFile(self):

        """ returns html/body + content """

        strResult = '<!doctype html public "-//IETF//DTD HTML 4.0//EN">'

        strResult += "<html>"

        strResult += "<head>"

        strResult += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>'

        strResult += "<title></title>"

        strResult += config.style

        strResult += "</head>\n<body>\n"

        if not self.fText:
            strResult += '<div style="text-align: center;margin: 40px;">' + self.toSVGGanttChart() + '</div>\n'
        else:
            strResult += '<pre>' + self.toHtmlTableOfContent() + '</pre>\n'

        strResult += self.toHtml()

        if not self.fText:
            strResult += '<section class="{}">'.format(__name__)
            strResult += '<div class="header">' + self.getTitleXML() + self.getDateString() + '</div>\n'
            strResult += '<div style="text-align: center;margin: 40px;">' + self.toSVGDiagram() + '</div>\n'
            strResult += '</section>\n'

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
            if type(c) is Period or type(c) is Cycle:
                strResult += '<section class="{}" id="{}">'.format(__name__, str(id(c)))

                strResult += '<div class="header">' + c.getTitleXML()
                if c.dateBegin is not None and c.dateEnd is not None:
                    strResult += c.getDateString()
                strResult += '</div>\n'

                strResult += '<pre>' + c.report() + '</pre>'

                if c.fPlot and (type(c) is Cycle or (type(c) is Period and c.getNumberOfCycles() > 0)):
                    strResult += '<div>'
                    strResult += c.plotAccumulationDuration()
                    strResult += c.plotAccumulation()
                    strResult += c.plotHist()
                    strResult += c.plotTimeDist()
                    strResult += c.toSVGGanttChart()
                    #strResult += c.toSVGDiagram()
                    strResult += '</div>'

                strResult += '</section>\n'

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
            if type(c) is Period or type(c) is Cycle:
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
            if type(c) is Period or type(c) is Cycle:
                strResult += "<td class='graph'>\n"
                strResult += c.plotAccumulationDuration()
                strResult += "</td>\n"

        strResult += "</tr>\n"

        strResult += "<tr>\n"

        for c in l:
            if type(c) is Period or type(c) is Cycle:
                strResult += "<td class='graph'>\n"
                strResult += c.plotAccumulation()
                strResult += "</td>\n"

        strResult += "</tr>\n"

        strResult += "<tr>\n"

        for c in l:
            if type(c) is Period or type(c) is Cycle:
                strResult += "<td class='graph'>\n"
                strResult += c.plotHist()
                strResult += "</td>\n"

        strResult += "</tr>\n"

        strResult += "<tr>\n"

        for c in l:
            if type(c) is Period or type(c) is Cycle:
                strResult += "<td class='graph'>\n"
                strResult += c.plotTimeDist()
                strResult += "</td>\n"

        strResult += "</tr>\n"

        strResult += "<tr>\n"

        for c in l:
            if type(c) is Period or type(c) is Cycle:
                strResult += "<td class='graph'>\n"
                strResult += c.toSVGGanttChart()
                strResult += "</td>\n"

        strResult += "</tr>\n"

        strResult += "</tbody>\n</table>\n"
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

        strResult += ' TEXT="' + self.getTitleXML()
        if self.dateBegin is not None and self.dateEnd is not None:
            strResult += '&#xa; ' + self.getDateString() + '&#xa;' + self.report().replace('\n','&#xa;')
        strResult += '">\n'

        strResult += '<font BOLD="true" NAME="Monospaced" SIZE="12"/>'

        strResult += self.getDescriptionFreemind()

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
            if type(c) is Cycle or type(c) is Period:
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

        l = self.getLength()
        strResult = '<g>'

        if self.color is not None and l > 0:
            strResult += '<rect fill="{}" x="{}" y="{}" height="{}" width="{}"/>\n'.format(self.color,1,y+1,((config.diagram_bar_height * 2) * l)-2,x+config.diagram_width-4)

        if not self.child:
            strResult += '<text x="{}" y="{}" style="vertical-align:top"><tspan x="10" dy="1.5em">{}</tspan><tspan x="10" dy="1.5em">{}</tspan></text>\n'.format(0,y,self.getTitleXML(), self.getDateString())
            strResult += '<line stroke="black" stroke-width=".5" stroke-dasharray="2,10" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(0,y,x+config.diagram_width,y)
            for d in range(0,l):
                strResult += '<line stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(x,y,x,y+config.diagram_bar_height)
                y += config.diagram_bar_height * 2
        else:
            for c in self.child:
                if type(c) is Cycle or type(c) is Period:
                    strResult += '<line stroke="black" stroke-width=".5" stroke-dasharray="2,10" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(0,y,config.diagram_width,y)
                    strResult += c.toSVG(x,y)
                    y += len(c) * config.diagram_bar_height * 2

        strResult += '</g>'

        return strResult


    def toSVGDiagram(self):

        """  """

        diagram_height = self.getLength() * (config.diagram_bar_height * 2) + 100
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

        if self.color is not None:
            c = self.color
        elif not self.child:
            # high level definition period
            c = '#aaffaa'
        else:
            c = '#aaaaff'

        strResult += '<a href="#{}">\n'.format(str(id(self)))
        strResult += '<rect fill="{}" opacity=".75" x="{}" y="{}" height="{}" width="{}" rx="2">\n'.format(c, x_i, y, config.diagram_bar_height*2, (l.days + 1) * 2)
        strResult += '<title>{}</title>\n'.format(self.getTitleXML() + self.getDateString() + '\n\n' + self.getDescriptionSVG() + '\n\n' + self.report())
        strResult += '</rect>'
        strResult += '<text x="{}" y="{}">{}</text>\n'.format(x_i + 2, y + 10,self.getTitleXML())
        strResult += '</a>\n'

        y_i = y + config.diagram_bar_height * 3
        for c in self.child:
            if type(c) is Cycle or type(c) is Period:
                strResult += c.toSVGGanttBar(dateBase,y_i)
                if type(c) is Period:
                    strResult += c.toSVGGantt(dateBase,y_i)
                y_i += config.diagram_bar_height * 3
                
        strResult += '<line stroke-dasharray="4" stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(x_i + (l.days + 1) * 2, y, x_i + (l.days + 1) * 2, y_i)

        strResult += '</g>'

        return strResult


    def toSVGGanttChart(self):

        """ Gantt chart of periods and cycles """

        if self.child:
            # detailed definition of period (Cycle and Period childs)
            d_0 = None
            d_1 = None
            for c in self.child:
                if type(c) is Cycle or type(c) is Period:
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

        strResult += '<g>'

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


    def CalendarYearPeriod(self,intYear,strArg=None):

        """ returns a plain calendar year period """

        try:
            date(intYear, 2, 29)
            self.append(Cycle(str(intYear),366))
        except ValueError:
            self.append(Cycle(str(intYear),365))

        if strArg is not None and strArg:
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

        if strArg is not None and strArg:
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

        if strArg is not None and strArg:
            self.setTitleStr(strArg)

        self.schedule(d)

        return self


    def CalendarMonthPeriod(self,intYear,strArg=None):

        """ returns a calendar year containing month periods """

        for m in range(1,13):
            if m > 11:
                d = date(intYear+1,1,1) - date(intYear,m,1)
            else:
                d = date(intYear,m+1,1) - date(intYear,m,1)

            self.append(Cycle('{}.{}'.format(intYear,m), d.days))

        if strArg is not None and strArg:
            self.setTitleStr(strArg)

        self.schedule(intYear)

        return self


    def CalendarLastWeeksPeriod(self,intWeek=26,strArg=None):

        """ returns a last weeks as periods """

        dt_0 = datetime.now().date()
        dt_i = dt_0 + timedelta(days=(7 - dt_0.weekday())) - timedelta(weeks=intWeek)
        self.dateFixed = dt_i

        for m in range(0,intWeek):
            self.append(Cycle(dt_i.strftime("%Y-W%U")))
            dt_i += timedelta(weeks=1)

        if strArg is not None and strArg:
            self.setTitleStr(strArg)

        self.schedule()

        return self


    def CalendarLastMonthsPeriod(self,intMonth=6,strArg=None):

        """ returns a last months (= 4 weeks) as periods """

        dt_0 = datetime.now().date()
        dt_i = dt_0 + timedelta(days=(7 - dt_0.weekday())) - timedelta(weeks = intMonth * 4)
        self.dateFixed = dt_i

        for m in range(0,intMonth):
            self.append(Cycle(dt_i.strftime("%Y-M%m"),4*7))
            dt_i += timedelta(weeks=4)

        if strArg is not None and strArg:
            self.setTitleStr(strArg)

        self.schedule()

        return self
