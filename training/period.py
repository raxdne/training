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

from datetime import timedelta, date, datetime, time, timezone

from suntime import Sun

from icalendar import Calendar, Event, Alarm

from training import config as config
from training.description import Description
from training.title import Title
from training.note import Note
from training.unit import Unit
from training.cycle import Cycle

#
#
#

class Period(Title,Description):

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

        self.setPlan()


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

        return self


    def appendChildDescription(self,objArg):

        """  """

        if len(self.child) > 0:
            self.child[len(self.child) - 1].appendDescription(objArg)


    def getDuration(self):

        """ return a timedelta """

        intResult = 0
        for u in self.child:
            if type(u) == Cycle:
                intResult += u.getDuration().total_seconds()

        return timedelta(seconds=intResult)


    def getNumberOfUnits(self):

        """  """

        intResult = 0
        for c in self.child:
            if type(c) == Cycle or type(c) == Period:
                intResult += c.getNumberOfUnits()

        return intResult


    def append(self,objArg):

        """  """

        if objArg == None or (type(objArg) != Cycle and type(objArg) != Period and type(objArg) != Note):
            print('error: ' + str(objArg), file=sys.stderr)
        else:
            self.child.append(objArg.dup())

        return self

    
    def insertByDate(self,objUnit,flagReplace=False):

        """  """

        objResult = None

        if objUnit != None and objUnit.dt != None:
            if len(self.child) < 1:
                # there is no child cycle yet
                delta = objUnit.dt.date() - self.dateBegin
                if delta.days > -1 and objUnit.dt.date() <= self.dateEnd:
                    l = self.dateEnd - self.dateBegin
                    c = Cycle(self.getTitleStr(), l.days + 1)
                    c.schedule(self.dateBegin.year,self.dateBegin.month,self.dateBegin.day)
                    objResult = c.insertByDate(objUnit)
                    if objResult != None:
                        self.append(c)
            else:
                for c in self.child:
                    if type(c) == Cycle or type(c) == Period:
                        objResult = c.insertByDate(objUnit,flagReplace)
                        if objResult != None:
                            break

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
            
            for c in self.child:
                if type(c) == Period:
                    if c.dateBegin <= objDate.date() and objDate.date() <= c.dateEnd:
                        return c.getPeriodByDate(objDate)
                elif type(c) == Cycle and c.getCycleByDate(objDate) != None:
                    return self

        return None


    def setPeriod(self, intArg):

        """  """

        self.periodInt = intArg

        return self


    def scale(self,floatScale,patternType=None):

        """  """

        for c in self.child:
            if type(c) == Cycle or type(c) == Period:
                c.scale(floatScale,patternType)

        return self


    def remove(self,patternType=None):

        """  """

        for c in self.child:
            if type(c) == Cycle or type(c) == Period:
                c.remove(patternType=patternType)

        return self


    def schedule(self, intYear=None, intMonth=None, intDay=None):

        """  """

        if self.dateBegin == None:

            if intYear == None and intMonth == None and intDay == None:
                if len(self.child) == 1:
                    print('info: set dates of period according to child', file=sys.stderr)
                    self.dateBegin = self.child[0].dateBegin
                    self.dateEnd = self.child[0].dateEnd
                elif len(self.child) > 1:
                    print('info: set dates of period according to childs', file=sys.stderr)
                    self.dateBegin = self.child[0].dateBegin
                    self.dateEnd = self.child[-1].dateEnd
                else:
                    print('error: cannot set dates according to childs', file=sys.stderr)
                    return None
            else:
                try:
                    if intMonth == None and intDay == None:
                        d = date(intYear, 1, 1)
                    elif intDay == None:
                        d = date(intYear, intMonth, 1)
                    else:
                        d = date(intYear, intMonth, intDay)
                except ValueError as e:
                    print('error: ' + str(e), file=sys.stderr)
                    return None

                e = d
                for c in self.child:
                    if type(c) == Cycle or type(c) == Period:
                        c.schedule(e.year, e.month, e.day)
                        e += timedelta(days=len(c))
                    elif type(c) == Note:
                        c.dt = e
                        #print('type: ' + c.dt.isoformat(), file=sys.stderr)

                self.dateBegin = d
                self.dateEnd = self.dateBegin + timedelta(days=(len(self) - 1))
        else:
            print('info: cannot set date again', file=sys.stderr)

        return self


    def stat(self, dictArg):

        """  """

        for c in self.child:
            if type(c) == Cycle or type(c) == Period:
                c.stat(dictArg)


    def report(self, dictArg=None):

        """  """

        if dictArg == None:
            dictArg = {}
            
        self.stat(dictArg)

        sum_h = 0.0
        for k in sorted(dictArg.keys()):
            sum_h += sum(dictArg[k][1])
        sum_h /= 3600
        
        strResult = ''
        for k in sorted(dictArg.keys()):
            # all registered kinds of units
            sum_k = sum(dictArg[k][1]) / 3600
            
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
        if n > 0:
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


    def toHtml(self):

        """  """

        strResult = '<section class="{}"'.format(__name__)

        if self.color != None:
            strResult += ' style="background-color: {}"'.format(self.color)

        strResult += '><div class="header">' + self.getTitleXML()
        if self.dateBegin != None and self.dateEnd != None:
            strResult += ' (' + str(len(self)) + ' ' + self.dateBegin.strftime("%Y-%m-%d") + ' .. ' + self.dateEnd.strftime("%Y-%m-%d") + ')'
        strResult += '</div>\n'

        strResult += '<ul>' + self.__listDescriptionToHtml__() + '</ul>'
        
        strResult += '<pre>' + self.report() + '</pre>'
        
        #strResult += '<svg baseProfile="full" height="600" version="1.1" width="1000" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink">' + self.toSVG(200,0) + '</svg>'

        for c in self.child:
            strResult += c.toHtml() + '\n'
            
        strResult += '</section>\n'

        return strResult


    def toHtmlFile(self):

        """ returns html/body + content """

        strResult = '<!doctype html public "-//IETF//DTD HTML 4.0//EN">'

        strResult += "<html>"

        strResult += "<head>"

        strResult += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>'
        
        strResult += "<title></title>"

        strResult += "<style>\nbody {font-family: Arial,sans-serif; font-size:12px; margin: 5px 5px 5px 5px;}\nsection {border-left: 1px dotted #aaaaaa;}\nsection > * {margin: 0px 0px 0px 2px;}\nsection > *:not(.header) {margin: 0.5em 0.5em 0.5em 2em;}\ndiv.header {font-weight:bold;}\nul, ol {padding: 0px 0px 0px 2em;}\npre {background-color: #f8f8f8;border: 1px solid #cccccc;padding: 6px 3px;border-radius: 3px;}</style>\n"

        strResult += "</head>"

        strResult += "<body>" + self.toHtml() + "</body>"

        strResult += "</html>"

        return strResult


    def toCSV(self):

        """  """

        strResult = '\n* ' + self.getTitleStr()
        if self.dateBegin != None and self.dateEnd != None:
            strResult += ' (' + str(len(self)) + ' ' + self.dateBegin.strftime("%Y-%m-%d") + ' .. ' + self.dateEnd.strftime("%Y-%m-%d") + ')'
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
            strResult += '&#xa; (' + self.dateBegin.strftime("%Y-%m-%d") + ' .. ' + self.dateEnd.strftime("%Y-%m-%d") + ')&#xa;' + self.report().replace('\n','&#xa;')
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
            strResult += c.toSqlite()
            
        return strResult


    def toSqliteDump(self):

        """  """
        
        strResult = 'PRAGMA journal_mode = OFF;\n\n'
        
        strResult += """CREATE TABLE IF NOT EXISTS "queries" (query text);

        INSERT INTO 'queries' VALUES (\"SELECT type FROM units;\");
        INSERT INTO 'queries' VALUES (\"SELECT count() AS Count, type AS Type FROM units GROUP BY type ORDER BY Count DESC;\");
        INSERT INTO 'queries' VALUES (\"SELECT sum(dist) AS Sum, type AS Type FROM units GROUP BY type ORDER BY Sum DESC;\");\n\n"""

        strResult += """CREATE TABLE IF NOT EXISTS "units" (
	"date"	TEXT,
	"dist"	REAL,
	"type"	TEXT,
	"duration"	INTEGER,
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
            strResult += '<text x="{}" y="{}" style="vertical-align:top"><tspan x="10" dy="1.5em">{}</tspan><tspan x="10" dy="1.5em">{}</tspan></text>\n'.format(0,y,self.getTitleXML(), '(' + self.dateBegin.strftime("%Y-%m-%d") + ' .. ' + self.dateEnd.strftime("%Y-%m-%d") + ')')
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
        strResult += '<title>{}</title>\n'.format(self.getTitleXML() + ' (' + self.dateBegin.strftime("%Y-%m-%d") + ' .. ' + self.dateEnd.strftime("%Y-%m-%d") + ')\n\n' + self.__listDescriptionToSVG__() + '\n\n' + self.report())
        strResult += '</rect>'
        strResult += '<text x="{}" y="{}">{}</text>\n'.format(x_i + 2, y + 10,self.getTitleXML())

        y_i = y + config.diagram_bar_height * 3
        for c in self.child:
            if type(c) == Cycle or type(c) == Period:
                strResult += c.toSVGGantt(dateBase,y_i)
                #if type(c) is period:
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
                elif d_1 == None:
                    d_1 = self.child[len(self.child) - 1].dateEnd

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

        # begin of spring
        d_1 = date(intYear,3,21)
        self.append(Cycle('Winter {}'.format(intYear), round((d_1 - d_0).total_seconds() / (24 * 60 * 60))))

        # begin of summer
        d_2 = date(intYear,6,21)
        self.append(Cycle('Spring {}'.format(intYear), round((d_2 - d_1).total_seconds() / (24 * 60 * 60))))

        # begin of autumn
        d_3 = date(intYear,9,21)
        self.append(Cycle('Summer {}'.format(intYear), round((d_3 - d_2).total_seconds() / (24 * 60 * 60))))

        # begin of winter
        d_4 = date(intYear,12,21)
        self.append(Cycle('Autumn {}'.format(intYear), round((d_4 - d_3).total_seconds() / (24 * 60 * 60))))

        # begin of next year
        d_5 = date(intYear+1,1,1)
        self.append(Cycle('Winter ' + str(intYear+1), round((d_5 - d_4).total_seconds() / (24 * 60 * 60))))

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
