#
# Data Management for Physical Training
#
# Copyright (C) 2021,2022 by Alexander Tenbusch
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

from datetime import timedelta, date, datetime, time, timezone

from suntime import Sun

from icalendar import Calendar, Event, Alarm

import training as config

from description import Description

from title import Title

from unit import Unit

from cycle import Cycle

#
#
#

class Period(Title,Description):

    def __init__(self,strArg=None,intArg=None):

        """ constructor """

        self.reset(strArg,intArg)


    def reset(self,strArg=None,intArg=None):

        """  """

        self.setTitleStr(strArg)
        self.setDescription()

        self.setPeriod(intArg)

        self.child = []
        self.dateBegin = None
        self.dateEnd = None

        return self


    def appendDescription(self,objArg):

        """  """

        if objArg != None and len(objArg) > 0:
            super().appendDescription(objArg)

        return self


    def resetDistances(self):

        """  """

        for c in self.child:
            c.resetDistances()

        return self


    def resetUnits(self,patternType=None):

        """  """

        for c in self.child:
            c.resetUnits(patternType)

        return self


    def appendChildDescription(self,objArg):

        """  """

        if len(self.child) > 0:
            self.child[len(self.child) - 1].appendDescription(objArg)


    def getNumberOfUnits(self):

        """  """

        intResult = 0
        for c in self.child:
            intResult += c.getNumberOfUnits()

        return intResult


    def getTypeOfUnits(self,arrArg=None):

        """  """

        if arrArg == None:
            arrArg = []
        for c in self.child:
            c.getTypeOfUnits(arrArg)

        return arrArg


    def append(self,objChild):

        """  """

        c = objChild.dup()
        self.child.append(c)

        return self

    
    def insertByDate(self,objUnit,flagReplace=False):

        """  """

        objResult = None

        if objUnit != None and objUnit.date != None:
            if len(self.child) < 1:
                # there is no child cycle yet
                delta = objUnit.date - self.dateBegin
                if delta.days > -1 and objUnit.date <= self.dateEnd:
                    l = self.dateEnd - self.dateBegin
                    c = cycle(self.getTitleStr(), l.days + 1)
                    c.schedule(self.dateBegin.year,self.dateBegin.month,self.dateBegin.day)
                    objResult = c.insertByDate(objUnit)
                    if objResult != None:
                        self.append(c)
            else:
                for c in self.child:
                    objResult = c.insertByDate(objUnit,flagReplace)
                    if objResult != None:
                        break

        return objResult


    def setPeriod(self, intArg):

        """  """

        self.periodInt = intArg

        return self


    def getPeriod(self):

        """  """

        l = 0
        for c in self.child:
            l += c.getPeriod()

        if self.periodInt == None or l > self.periodInt:
            self.setPeriod(l)

        return self.periodInt


    def scale(self,floatScale,patternType=None):

        """  """

        for c in self.child:
            c.scale(floatScale,patternType)

        return self


    def schedule(self, intYear, intMonth, intDay):

        """  """

        if self.dateBegin == None:
            try:
                d = date(intYear, intMonth, intDay)
            except:
                return None

            for c in self.child:
                c.schedule(d.year, d.month, d.day)
                d += timedelta(days=c.getPeriod())

            self.dateBegin = date(intYear, intMonth, intDay)
            self.dateEnd = self.dateBegin + timedelta(days=(self.getPeriod() - 1))

        return self


    def report(self, arrArg=None):

        """  """

        if arrArg == None:
            arrArg = {}
        strResult = ''

        for c in self.child:
            c.report(arrArg)

        sum_h = 0.0
        for k in sorted(arrArg.keys()):
            if arrArg[k][0] == None or arrArg[k][0] < 0.01:
                strResult += "{:4} x {:3} {:5}    {:5.0f} h\n".format(arrArg[k][1], k, ' ', round(arrArg[k][2] / 3600, 1))
            else:
                strResult += "{:4} x {:3} {:5.0f} {} {:5.0f} h\n".format(arrArg[k][1], k, arrArg[k][0], config.unit_distance, round(arrArg[k][2] / 3600, 1))        
            sum_h += arrArg[k][2]

        sum_h /= 3600.0
        n = self.getNumberOfUnits()
        if n > 0:
            p = self.getPeriod()
            #strResult += "{:4} Units in {} Days = {:4.01f} Units/Week\n".format(n, p, n/p * 7.0)
            strResult += "{:4} h     in {} Days = {:4.01f} h/Week\n".format(round(sum_h), p, sum_h/p * 7.0)

        return strResult


    def stat(self, arrArg=None):

        """  """

        t = sorted(self.getTypeOfUnits())
        if arrArg == None:
            arrArg = []
            for m in range(12):
                a = {}
                for u in t:
                    a[u] = 0.0
                arrArg.append(a)

        strResult = self.getTitleStr() + '\n'

        for c in self.child:
            c.stat(arrArg)

        for u in t:
            strResult += "\t{}".format(u)

        for m in range(12):
            strResult += "\n{}".format(m+1)
            for u in arrArg[m]:
                strResult += "\t{:.0f}".format(arrArg[m][u])

        return strResult


    def parseFile(self,listFilename,fUpdater=None):

        """  """

        if type(listFilename) == str:
            listFilename = [listFilename]

        a = []
        d0 = None
        d1 = None
        t = unit()

        for filename in listFilename:
            print("* ",filename, file=sys.stderr)
            with open(filename) as f:
                content = f.read().splitlines()
            f.close()

            for l in content:
                if l == None or l == '':
                    pass
                elif ((fUpdater != None and t.parse(fUpdater(l))) or t.parse(l)) and t.date != None:
                    if d0 == None or t.date < d0:
                        d0 = t.date
                    if d1 == None or t.date > d1:
                        d1 = t.date
                    a.append(t)
                    t = unit()
                else:
                    print('error: ' + l, file=sys.stderr)

        print('Report {} .. {}'.format(d0.isoformat(),d1.isoformat()), file=sys.stderr)

        delta = d1 - d0

        if len(self.child) > 0:
            # there is a child list already
            pass
        elif delta.days < 365:
            for y in range(d0.year,d1.year+1):
                self.append(CalendarWeekPeriod(y))
        elif delta.days < 3 * 365:
            for y in range(d0.year,d1.year+1):
                self.append(CalendarMonthPeriod(y))
        else:
            for y in range(d0.year,d1.year+1):
                self.append(CalendarYearPeriod(y))

        for t in a:
            #print(t.toString())
            self.insertByDate(t)

        return self


    def dup(self):

        """  """

        return copy.deepcopy(self)


    def toString(self):

        """  """

        strResult = '\n* ' + self.getTitleStr() + ' (' + str(self.getPeriod()) + ' ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n\n'

        strResult += self.__listDescriptionToString__()

        for c in self.child:
            strResult += c.toString() + '\n'
            
        return strResult


    def toPlain(self):

        return self.toString() + '\n'


    def toHtml(self):

        """  """

        strResult = '<section class="period">'

        strResult += '<div class="header">' + self.getTitleStr() + ' (' + str(self.getPeriod()) + ' ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '</div>\n'

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

        strResult = '\n* ' + self.getTitleStr() + ' (' + str(self.getPeriod()) + ' ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n'
        for c in self.child:
            strResult += c.toCSV() + '\n'

        return strResult


    def toXML(self):

        """  """

        strResult = '<node'
        if self.getNumberOfUnits() < 1:
           strResult += ' BACKGROUND_COLOR="{}"'.format('#ffaaaa')
        else:
            strResult += ' FOLDED="{}"'.format('false')

        strResult += ' TEXT="' + self.getTitleStr() + '&#xa; (' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')&#xa;' + self.report().replace('\n','&#xa;') + '">\n'
        strResult += '<font BOLD="true" NAME="Monospaced" SIZE="12"/>'

        strResult += self.__listDescriptionToXML__()

        for c in self.child:
            strResult += c.toXML()
        strResult += '</node>\n'

        return strResult


    def toFreeMind(self):

        """  """

        strResult = '<map>\n'
        strResult += self.toXML()
        strResult += '</map>\n'

        return strResult


    def toSVG(self, x = config.diagram_offset, y=20):

        """  """

        strResult = '<g>'

        if len(self.child) < 1:
            strResult += '<text x="{}" y="{}" style="vertical-align:top"><tspan x="10" dy="1.5em">{}</tspan><tspan x="10" dy="1.5em">{}</tspan></text>\n'.format(0,y,self.getTitleStr(), '(' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')')
            strResult += '<line stroke="black" stroke-width=".5" stroke-dasharray="2,10" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(0,y,x+config.diagram_width,y)
            for d in range(0,self.getPeriod()):
                strResult += '<line stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(x,y,x,y+config.diagram_bar_height)
                y += config.diagram_bar_height * 2
        else:
            for c in self.child:
                #strResult += '<line stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(x,y,x+400,y)
                #strResult += '<text x="{}" y="{}">{}</text>\n'.format(x+400,y,c.getTitleStr())
                strResult += c.toSVG(x,y)
                y += c.getPeriod() * config.diagram_bar_height * 2

        strResult += '</g>'

        return strResult


    def toSVGDiagram(self):

        """  """

        diagram_height = self.getPeriod() * (config.diagram_bar_height * 2) + 100
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
            return '<text x="{}" y="{}">{}</text>\n'.format(0 + 2, y + 10,self.getTitleStr())

        strResult = '<g>'

        strResult += '<rect fill="{}" opacity=".75" x="{}" y="{}" height="{}" width="{}" rx="2">\n'.format('#aaaaff', x_i, y, config.diagram_bar_height*2, (l.days + 1) * 2)
        strResult += '<title>{}</title>\n'.format(self.getTitleStr() + ' (' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ') ' + self.__listDescriptionToString__())
        strResult += '</rect>'
        strResult += '<text x="{}" y="{}">{}</text>\n'.format(x_i + 2, y + 10,self.getTitleStr())

        y_i = y + config.diagram_bar_height * 3
        for c in self.child:
            strResult += c.toSVGGantt(dateBase,y_i)
            #if type(c) is period:
            y_i += config.diagram_bar_height * 3

        strResult += '<line stroke-dasharray="4" stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(x_i + (l.days + 1) * 2, y, x_i + (l.days + 1) * 2, y_i)

        strResult += '</g>'

        return strResult


    def toSVGGanttChart(self):

        """ Gantt chart of periods and cycles """

        d_0 = self.child[0].dateBegin
        d_1 = self.child[len(self.child) - 1].dateEnd

        diagram_height = 40 * (config.diagram_bar_height * 2) + 100
        try:
            diagram_width = ((d_1 - d_0).days) * 2 + 100
        except:
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
            strResult += '<title>{}</title>\n'.format(d_i.isoformat())
            strResult += '</line>'
            strResult += '<g transform="translate({},{})">'.format(w+8, diagram_height - 105)
            strResult += '<g transform="rotate(-45)">'
            strResult += '<text x="{}" y="{}">{}</text>\n'.format(0, 0, d_i.isoformat())
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


    def toiCalString(self):

        """  """

        e = self.dateEnd + timedelta(days=1)

        if len(self.child) < 1:
            strResult = "BEGIN:VEVENT\nSUMMARY:Period {title}\nDTSTART;{y:04}{m:02}{d:02}\nDTEND;{ye:04}{me:02}{de:02}\nDTSTAMP;{y:04}{m:02}{d:02}\nEND:VEVENT\n".format(title=self.getTitleStr(), y=self.dateBegin.year, m=self.dateBegin.month, d=self.dateBegin.day, ye=e.year, me=e.month, de=e.day)
        else:
            strResult = ''
            for c in self.child:
                strResult += c.toiCalString()

        return strResult


    def to_ical(self,cal):

        """  """

        #event = Event()
        #event.add('summary', 'Period: {}'.format(self.getTitleStr()))
        #event.add('dtstart', self.dateBegin)
        #event.add('dtend', self.dateEnd + timedelta(days=1))
        #event.add('dtstamp', datetime.now().astimezone(None))
        #cal.add_component(event)

        for c in self.child:
            c.to_ical(cal)


    def toVCalendar(self):

        """  """

        try:
            cal = Calendar()
            cal.add('prodid', '-//{title}//  //'.format(title=self.getTitleStr()))
            cal.add('version', '2.0')
            self.to_ical(cal)
            return cal.to_ical()
        except NameError:
            # TODO: remove all toiCalString() legacy code
            strResult = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//{title}//  //\n".format(title=self.getTitleStr())
            for c in self.child:
                strResult += c.toiCalString()
            strResult += "END:VCALENDAR"
            return strResult


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


if __name__ == "__main__":
    
    print('Module Test:\n')
    
    # p = Period('General Basics')
    # p.appendDescription('Regeneration')

    # c = Cycle('General Endurance')
    # c.insert(1,Unit('18:00;3.5;RB;25:00'))
    # c.insert(3,Unit('18:00;3.5;RB;25:00'))
    # f = c.insert(4,Unit(';FB;25:00'))
    # c.insert(5,Unit(';FB;25:00'))
    # c.insert(6,Unit('08:00;30;BB;02:00:00'))

    # p.append(c)
    # p.append(c)
    # c.scale(1.2,r"FB")
    # p.append(c)

    # c.appendDescription('Nutrition ABC')
    # f.appendDescription('Maximum')
    
    # p.append(c)
    # p.append(c)
    # f.setDescription()
    # p.append(c)

    # p.schedule(2022,3,4)

    #print(p.toSVGGanttChart())
    
    #p = Period('Plan').CalendarWeekPeriod(2022)
    #p = Period('Plan').CalendarYearPeriod(2023)
    p = Period('Plan').CalendarMonthPeriod(2025)
    #p = Period('Plan').CalendarSeasonPeriod(2025)
    p.insertByDate(Unit('2025-03-03T8:00:00+2;100;RG;5h'))
    
    print(p.toString())
    
