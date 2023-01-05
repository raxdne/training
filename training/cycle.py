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

from statistics import mean

from datetime import timedelta, date, datetime, time

from icalendar import Calendar, Event, Alarm

from training import config as config
from training.description import Description
from training.title import Title
from training.unit import Unit
#from training.cycle import Cycle
#from training.period import Period

#
#
#

class Cycle(Title,Description):

    def __init__(self,strArg=None,intArg=7):

        """ constructor """

        self.reset(strArg,intArg)


    def reset(self,strArg=None,intArg=7):

        """  """

        self.setTitleStr(strArg)
        self.setDescription()

        self.periodInt = intArg

        self.day = []
        for i in range(0,int(intArg)):
            self.day.append([])

        self.dateBegin = None
        self.dateEnd = None

        self.color = None

        return self


    def appendDescription(self,objArg):

        """  """

        if objArg != None and len(objArg) > 0:
            super().appendDescription(objArg)

        return self


    def resetDistances(self):

        """  """

        for v in self.day:
            for u in v:
                u.setDistStr(None)

        return self


    def resetUnits(self,patternType=None):

        """  """

        if patternType == None:
            for v in self.day:
                del v[0:]
        else:
            for v in self.day:
                # due to modification of the array iterator is not usable
                i = 0
                j = len(v)
                while i < j:
                    if v[i].type != None and re.match(patternType,v[i].type):
                        v.pop(i)
                        j -= 1
                    else:
                        i += 1

        return self


    def setColor(self,strColor):

        """  """

        if strColor != None and len(strColor) > 0:
            self.color = strColor

        return self


    def getLength(self):

        """  """

        return len(self.day)


    def combine(self,objUnit,intPause=0):

        """  """

        # find last unit
        for i in range(len(self.day)-1,0,-1):
            if len(self.day[i]) > 0:
                objUnit.combined = True
                objUnit.pause = timedelta(minutes=intPause)
                return self.insert(i,objUnit)
        
        return None


    def shift(self,intIndexA,intIndexB,flagReplace=False):

        """  """

        if intIndexA > -1 and intIndexB > -1 and intIndexA < len(self.day) and intIndexB < len(self.day) and intIndexA != intIndexB:
            if flagReplace:
                # override exisiting
                self.day[intIndexB] = self.day[intIndexA]
            else:
                self.day[intIndexB] += self.day[intIndexA]

            self.day[intIndexA] = []

        return self


    def swap(self,intIndexA,intIndexB):

        """  """

        if intIndexA > -1 and intIndexB > -1 and intIndexA < len(self.day) and intIndexB < len(self.day) and intIndexA != intIndexB:
            t = self.day[intIndexB]
            self.day[intIndexB] = self.day[intIndexA]
            self.day[intIndexA] = t

        return self


    def insert(self,intIndex,objUnit,flagReplace=False):

        """  """

        objResult = None

        if objUnit != None and intIndex > -1 and intIndex < len(self.day):
            objResult = objUnit.dup()
            if flagReplace:
                # override exisiting
                self.day[intIndex] = [objResult]
            else:
                self.day[intIndex].append(objResult)

        return self


    def insertByDate(self,objUnit,flagReplace=False):

        """  """

        objResult = None

        if objUnit != None and objUnit.dt != None:
            delta = objUnit.dt.date() - self.dateBegin
            if delta.days > -1 and objUnit.dt.date() <= self.dateEnd:
                objResult = objUnit.dup()
                if flagReplace:
                    # override exisiting
                    self.day[delta.days] = [objResult]
                else:
                    self.day[delta.days].append(objResult)

        return self


    def insertDescriptionStr(self,intIndex,strArg):

        """  """

        if strArg == None or strArg == '':
            pass
        elif len(self.day) > intIndex and len(self.day[intIndex]) > 0:
            self.day[intIndex][len(self.day[intIndex]) - 1].appendDescription(strArg)


    def getPeriod(self):

        """  """

        return len(self.day)


    def getPeriodDone(self):

        """  """

        if self.dateBegin != None and date.today() >= self.dateBegin and self.dateEnd != None and date.today() <= self.dateEnd:
            return (date.today() - self.dateBegin).days + 1
        else:
            return len(self.day)


    def getNumberOfUnits(self):

        """  """

        intResult = 0
        for v in self.day:
            for u in v:
                if u.type != None and len(u.type) > 0:
                    intResult += 1

        return intResult


    def getDurationOfUnits(self):

        """ in minutes """

        intResult = 0
        for v in self.day:
            for u in v:
                if u.type != None and len(u.type) > 0 and u.duration != None and u.duration.total_seconds() > 59:
                    intResult += u.duration.total_seconds()

        return intResult / 60


    def getTypeOfUnits(self,arrArg=None):

        """  """

        if arrArg == None:
            arrArg = []

        for v in self.day:
            for u in v:
                if u.type != None and len(u.type) > 0:
                    if u.type in arrArg:
                        pass
                    else:
                        arrArg.append(u.type)

        return arrArg


    def scale(self,floatScale,patternType=None):

        """  """

        for v in self.day:
            for u in v:
                u.scale(floatScale,patternType)

        return self


    def schedule(self, intYear, intMonth, intDay):

        """  """

        if self.dateBegin == None:
            try:
                d = date(intYear, intMonth, intDay)
            except ValueError as e:
                print('error: ' + str(e), file=sys.stderr)
                return self

            m = len(self.day)
            h = 0
            while h < m:

                #print('day: ' + str(h), file=sys.stderr)
                
                if config.sun != None:
                    # fix 't' according to sunrise/sunset
                    t_earliest = config.sun.get_local_sunrise_time(d + timedelta(days=h)) + timedelta(seconds=config.twilight)
                    t_latest   = config.sun.get_local_sunset_time(d + timedelta(days=h))  - timedelta(seconds=config.twilight)

                # count units of this day
                n = len(self.day[h])
                i = 0
                while i < n:

                    #print('u: ' + str(i), file=sys.stderr)

                    if self.day[h][i].clock == None:
                        d_i = datetime.combine(d + timedelta(days=h),time(0)).astimezone(None)
                        self.day[h][i].dt = d_i
                    else:
                        d_i = datetime.combine(d + timedelta(days=h), self.day[h][i].clock).astimezone(None)
                        
                        if config.sun != None:
                            # fix 't' according to sunrise/sunset
                            if t_earliest > d_i:
                                #print('too early: ' + str(d_i.isoformat()), file=sys.stderr)
                                # shift start time after twilight
                                self.day[h][i].dt = t_earliest
                                # adjust to 15min steps
                                self.day[h][i].dt -= timedelta(minutes=(self.day[h][i].dt.minute % 15))
                            elif t_latest < d_i + self.day[h][i].duration:
                                #print('too late: ' + str(d_i.isoformat()), file=sys.stderr)
                                # shift end time before twilight
                                self.day[h][i].dt = t_latest - self.day[h][i].duration
                                self.day[h][i].dt -= timedelta(minutes=(self.day[h][i].dt.minute % 15))
                            else:
                                # use defined time
                                self.day[h][i].dt = d_i
                        else:
                            self.day[h][i].dt = d_i
                            
                        self.day[h][i].clock = None
                        
                    if self.day[h][i].duration != None:
                        d_i += self.day[h][i].duration
                            
                    # count number of combined units
                    j = i+1
                    while j < n and self.day[h][j].combined:
                        j += 1

                    if j > i+1:
                        # combined units
                        print('{} combined units'.format(j-i), file=sys.stderr)

                        k = i+1
                        while k < j:
                            d_i += self.day[h][k].pause
                            self.day[h][k].dt = d_i
                            d_i += self.day[h][k].duration
                            k += 1
                        i = k
                        # TODO: fix start time of all combined units according to t_latest
                    else:
                        # no combined units
                        i += 1

                h += 1

            self.dateBegin = date(intYear, intMonth, intDay)
            self.dateEnd = self.dateBegin + timedelta(days=(self.getPeriod() - 1))

        return self
    

    def stat(self, arrArg):

        """  """

        for v in self.day:
            for u in v:
                if u.dist == None or u.type == None or len(u.type) < 1:
                    pass
                else:
                    arrArg[u.dt.month - 1][u.type] += u.dist


    def report(self, arrArg=None):

        """  """

        if arrArg == None:
            arrArg = {}

        strResult = ''

        sum_h = 0.0
        for v in self.day:
            for u in v:
                if u.type != None and len(u.type) > 0 and u.duration != None:
                    if u.type not in arrArg:
                        arrArg[u.type] = [[],[]]
                    if u.dist != None:
                        arrArg[u.type][0].append(u.dist)
                    else:
                        arrArg[u.type][0].append(0)
                    arrArg[u.type][1].append(u.duration.total_seconds())
                    sum_h += u.duration.total_seconds()
        sum_h /= 3600.0

        for k in sorted(arrArg.keys()):
            if len(arrArg[k][0]) < 1:
                strResult += "{:4} x {:3} {:7}    {:7.01f} h\n".format(len(arrArg[k][0]), k, ' ', round(sum(arrArg[k][1]) / 3600, 2))
            elif len(arrArg[k][0]) < 3:
                strResult += "{:4} x {:3} {:7.01f} {} {:7.01f} h\n".format(len(arrArg[k][0]), k, sum(arrArg[k][0]), config.unit_distance, round(sum(arrArg[k][1]) / 3600, 2))
            else:
                strResult += "{:4} x {:3} {:7.01f} {} {:7.01f} h {:5.01f} /{:5.01f} /{:5.01f}\n".format(len(arrArg[k][0]), k, sum(arrArg[k][0]), config.unit_distance, round(sum(arrArg[k][1]) / 3600, 2), min(arrArg[k][0]), mean(arrArg[k][0]), max(arrArg[k][0]))

        n = self.getNumberOfUnits()
        if n > 0:
            p = self.getPeriodDone()
            strResult += "\n{} Units {:.2f} h in {} Days ≌ {:.2f} h/Week ≌ {:.0f} min/d\n".format(n, round(sum_h,2), p, sum_h * 7.0 / p, sum_h * 60 / p)

        return strResult


    def dup(self):

        """  """

        return copy.deepcopy(self)


    def toString(self):

        """  """

        strResult = '\n** ' + self.getTitleStr() + ' (' + str(self.getPeriod()) + ', ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n\n'
        for v in self.day:
            for u in v:
                strResult += u.toString() + '\n'

        return strResult


    def toHtml(self):

        """  """
        
        strResult = '<section class="cycle"'

        if self.color != None:
            strResult += ' style="background-color: {}"'.format(self.color)

        strResult += '><div class="header">' + self.getTitleStr() + ' (' + str(self.getPeriod()) + ', ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '</div>\n'

        strResult += '<ul>' + self.__listDescriptionToHtml__() + '</ul>'
        
        for v in self.day:
            for u in v:
                strResult += '<p class="unit"'
                if u.type != None and len(u.type) > 0 and u.type[0] in config.colors:
                    strResult += ' style="background-color: ' + config.colors[u.type[0]] + '"'

                strResult += '>' + u.toString() + ' ' + u.__listDescriptionToString__() + '</p>\n'

        #strResult += '<svg baseProfile="full" height="200" version="1.1" width="800" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink">' + self.toSVG(200,0) + '</svg>'

        strResult += '<pre>' + self.report() + '</pre>'
        
        strResult += '</section>'

        return strResult


    def toCSV(self):

        """  """

        strResult = '\n* ' + self.getTitleStr() + ' (' + str(self.getPeriod()) + ', ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n'
        for v in self.day:
            for u in v:
                strResult += u.toCSV() + '\n'

        return strResult


    def toSVG(self,x,y):

        """  """

        strResult = '<g>'

        strResult += '<line stroke="black" stroke-width=".5" stroke-dasharray="2,10" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(0,y,x+config.diagram_width,y)

        if self.color != None:
            strResult += '<rect fill="{}" x="{}" y="{}" height="{}" width="{}"/>\n'.format(self.color,1,y+1,((config.diagram_bar_height * 2)*len(self.day))-2,x+config.diagram_width-4)

        strResult += '<text x="{}" y="{}" style="vertical-align:top" text-anchor="right"><tspan x="10" dy="1.5em">{}</tspan><tspan x="10" dy="1.5em">{}</tspan><title>{}</title></text>\n'.format(0,y,self.getTitleStr(), '(' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ') ', (self.getTitleStr() + ' (' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')\n\n' + self.__listDescriptionToString__() + '\n\n' + self.report()))

        if len(self.day) < 1:
            pass
        else:
            y += config.diagram_bar_height / 2
            t = date.today()
            d = self.dateBegin
            for v in self.day:
                strResult += '<line stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(x,y,x,y+config.diagram_bar_height)

                if d.month == t.month and d.day == t.day:
                    strResult += '<rect fill="{}" x="{}" y="{}" height="{}" width="{}"/>\n'.format('#ffaaaa',x,y-1,config.diagram_bar_height+2,config.diagram_width - config.diagram_offset)
                    if d.year == t.year:
                        strResult +=  '<foreignObject x="{}" y="{}" height="{}" width="{}"><a xmlns="http://www.w3.org/1999/xhtml" name="today"/></foreignObject>\n'.format(x,y-1,config.diagram_bar_height+2,config.diagram_width - config.diagram_offset)
                elif d.isoweekday() == 6 or d.isoweekday() == 7:
                    strResult += '<rect fill="{}" x="{}" y="{}" height="{}" width="{}"/>\n'.format('#eeeeee',x,y-1,config.diagram_bar_height+2,config.diagram_width - config.diagram_offset)
                d += timedelta(days=1)

                x_i = x

                for u in v:
                    # all units first
                    if u.duration != None:
                        if not u.combined and v.index(u) > 0:
                            x_i += 2
                        elif u.combined and u.pause.total_seconds() > 0:
                            x_i += u.pause.total_seconds() / 3600 * 25 * config.diagram_scale_dist
                        strResult += u.toSVG(x_i,y)
                        x_i += u.duration.total_seconds() / 3600 * 25 * config.diagram_scale_dist

                for u in v:
                    # all remarks after
                    if u.duration == None:
                        strResult += u.toSVG(x_i,y)
                        x_i += len(u.toString()) * config.font_size

                y += config.diagram_bar_height * 2

        strResult += '</g>'

        return strResult


    def toSVGGantt(self,dateBase,y=0):

        """  """
    
        try:
            l = self.getPeriodDone()
            x_i = (self.dateBegin - dateBase).days * 2
        except ValueError as e:
            print('error: ' + str(e), file=sys.stderr)
            return ''
        
        strResult = '<g>'

        if self.color == None:
            color = '#ffaaaa'
        else:
            color = self.color
            
        strResult += '<rect opacity=".75" stroke="red" stroke-width=".5" fill="{}" x="{}" y="{}" height="{}" width="{}" rx="2">\n'.format(color, x_i, y, config.diagram_bar_height*2, l * 2)
        strResult += '<title>{}</title>\n'.format(self.getTitleStr() + ' (' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ') ' + self.__listDescriptionToString__())
        strResult += '</rect>'

        # TODO: make config.diagram_height configurable
        config.diagram_height = 40 * (config.diagram_bar_height * 2) + 100

        h = round(self.getDurationOfUnits() / l)

        if self.color != None:
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
            
        strResult += '<rect opacity=".75" stroke="{}" stroke-width=".5" fill="{}" x="{}" y="{}" height="{}" width="{}">\n'.format(scolor, color, x_i + 1, config.diagram_height - h - 10, h, l * 2 - 2)
        strResult += '<title>{}</title>\n'.format(self.getTitleStr() + ' (' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')\n\n' + self.__listDescriptionToString__() + '\n\n' + self.report())
        strResult += '</rect>'

        #strResult += '<text x="{}" y="{}">{}</text>\n'.format(x_i,y,self.getTitleStr())
        strResult += '</g>'

        return strResult


    def toXML(self):

        """  """

        strResult = '<node'

        if self.color != None:
            strResult += ' BACKGROUND_COLOR="{}"'.format(self.color)
        elif self.getNumberOfUnits() < 1:
            strResult += ' BACKGROUND_COLOR="{}"'.format('#ffaaaa')
        else:
            strResult += ' FOLDED="{}"'.format('true')

        strResult += ' TEXT="' + self.getTitleStr() + '&#xa;(' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')&#xa;' + self.report().replace('\n','&#xa;') + '">\n'
        strResult += '<font BOLD="false" NAME="Monospaced" SIZE="12"/>'

        strResult += self.__listDescriptionToXML__()

        for v in self.day:
            # count units of this day
            n = len(v)
            i = 0
            while i < n:

                # count number of combined units
                j = i+1
                while j < n and v[j].combined:
                    j += 1

                if j > i+1:
                    # combined units
                    strResult += '<node TEXT="{}">\n'.format('Block')
                    k = i
                    while k < j:
                        if v[k].pause.total_seconds() > 0:
                            strResult += '<node TEXT="{}"/>\n'.format('Pause for ' + str(v[k].pause.total_seconds() / 60) + 'min')
                        strResult += v[k].toXML()
                        k += 1
                    i = k
                    strResult += '</node>\n'
                else:
                    # no combined units
                    strResult += v[i].toXML()
                    i += 1
                        
        strResult += '</node>\n'

        return strResult


    def to_ical(self,cal):

        """  """

        event = Event()
        event.add('summary', 'Cycle: {}'.format(self.getTitleStr()))
        event.add('dtstart', self.dateBegin)
        event.add('dtend', self.dateEnd + timedelta(days=1))
        event.add('dtstamp', datetime.now().astimezone(None))
        cal.add_component(event)

        for v in self.day:
            for u in v:
                u.to_ical(cal)


if __name__ == "__main__":
    
    print('Module Test:\n')
    
    c = Cycle('C1',2*7)

    c.insert(1,Unit('18:00;3.5;RB;25:00'))
    c.insert(3,Unit('18:00;3.5;RB;25:00'))
    c.combine(Unit(';FB;25:00'))
    c.insert(5,Unit(';FB;25:00'))
    c.insert(6,Unit('08:00;30;BB;02:00:00'))
    c.insert(8,Unit(';FB;25:00'))
    c.insert(10,Unit(';FB;25:00'))
    c.insert(13,Unit('08:00;30;BB;02:00:00'))

    c.schedule(2022,3,1)
    c.schedule(2023,3,1)
    c.insertByDate(Unit('2022-03-03T8:00:00+2;100;RG;5h'), True)

    print(c.toString())

    print(c.toSVG(0,0))
