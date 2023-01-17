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
from training.note import Note
from training.unit import Unit
from training.pause import Pause
from training.combination import Combination

#
#
#

class Cycle(Title,Description):

    def __init__(self,strArg=None,intArg=7):

        """  """

        super(Title, self).__init__()
        super(Description, self).__init__()
        
        self.setTitleStr(strArg)
        self.setDescription()

        self.day = []
        for i in range(0,int(intArg)):
            self.day.append([])

        self.dateBegin = None
        self.dateEnd = None

        self.color = None


    def __len__(self):

        """  """

        return len(self.day)


    def __str__(self):

        """  """

        strResult = '\n** ' + super().getTitleStr() + ' (' + str(len(self)) + ', ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n\n'
        for v in self.day:
            for u in v:
                strResult += str(u) + '\n'

        return strResult


    def appendDescription(self,objArg):

        """  """

        if objArg != None and len(objArg) > 0:
            super().appendDescription(objArg)

        return self


    def resetDistances(self):

        """  """

        for i in range(len(self)):
            self.day[i] = []
            
        return self


    def remove(self,intIndexA=-1,patternType=None):

        """  """

        if intIndexA > -1 and intIndexA < len(self):
            if patternType != None:
                # delete only matching elements in list of indexed day
                dayNew = []
                for u in self.day[intIndexA]:
                    if u.type == None or re.match(patternType,u.type):
                        # to be ignored
                        pass
                    else:
                        dayNew.append(u.dup())
                self.day[intIndexA] = copy.deepcopy(dayNew)
            else:
                # delete whole list of indexed day
                self.day[intIndexA] = []
        elif patternType != None:
            # whole cycle using pattern
            daysNew = []
            for i in range(0,len(self)):
                daysNew.append([])
                for u in self.day[i]:
                    if type(u) == Unit and (u.type == None or re.match(patternType,u.type)):
                        pass
                    else:
                        daysNew[i].append(u)
            self.day = daysNew
            
        return self


    def shift(self,intIndexA,intIndexB,flagReplace=False):

        """  """

        if intIndexA > -1 and intIndexB > -1 and intIndexA < len(self) and intIndexB < len(self) and intIndexA != intIndexB:
            self.copy(intIndexA,intIndexB,flagReplace)
            self.remove(intIndexA)

        return self


    def copy(self,intIndexA,intIndexB,flagReplace=False):

        """  """

        if intIndexA > -1 and intIndexB > -1 and intIndexA < len(self) and intIndexB < len(self) and intIndexA != intIndexB:
            objCopy = copy.deepcopy(self.day[intIndexA])
            if flagReplace:
                # override exisiting
                self.day[intIndexB] = objCopy
            else:
                self.day[intIndexB] += objCopy

        return self


    def swap(self,intIndexA,intIndexB):

        """  """

        if intIndexA > -1 and intIndexB > -1 and intIndexA < len(self) and intIndexB < len(self) and intIndexA != intIndexB:
            t = self.day[intIndexB]
            self.day[intIndexB] = self.day[intIndexA]
            self.day[intIndexA] = t

        return self


    def insert(self,intIndex,objArg,flagReplace=False):

        """  """

        objResult = None

        if objArg == None:
            pass
        elif type(intIndex) == list:
            for i in intIndex:
                self.insert(i,objArg,flagReplace)
            return []
        elif type(objArg) == list:
            for u in objArg:
                self.insert(intIndex,u,flagReplace)
            return []
        elif intIndex > -1 and intIndex < len(self):
            objResult = objArg.dup()
            if flagReplace:
                # override exisiting
                self.day[intIndex] = [objResult]
            else:
                self.day[intIndex].append(objResult)

        return objResult


    def insertByDate(self,objArg,flagReplace=False):

        """  """

        objResult = None

        if objArg != None and objArg.dt != None:
            delta = objArg.dt.date() - self.dateBegin
            if delta.days > -1 and objArg.dt.date() <= self.dateEnd:
                objResult = objArg.dup()
                if flagReplace:
                    # override exisiting
                    self.day[delta.days] = [objResult]
                else:
                    self.day[delta.days].append(objResult)

        return objResult


    def insertDescriptionStr(self,intIndex,strArg):

        """  """

        if strArg == None or strArg == '':
            pass
        elif len(self) > intIndex and len(self.day[intIndex]) > 0:
            self.day[intIndex][len(self.day[intIndex]) - 1].appendDescription(strArg)

        return self

    
    def getPeriodDone(self):

        """  """

        if self.dateBegin != None and date.today() >= self.dateBegin and self.dateEnd != None and date.today() <= self.dateEnd:
            return (date.today() - self.dateBegin).days + 1
        else:
            return len(self)


    def getNumberOfUnits(self):

        """  """

        intResult = 0
        for v in self.day:
            for u in v:
                if type(u) == Combination:
                    intResult += u.getNumberOfUnits()
                elif type(u) == Unit and u.type != None and len(u.type) > 0:
                    intResult += 1

        return intResult


    def getDuration(self):

        """ return a timedelta """

        intResult = 0
        for v in self.day:
            for u in v:
                if (type(u) == Unit or type(u) == Combination):
                    intResult += u.getDuration().total_seconds()

        return timedelta(seconds=intResult)


    def scale(self,floatScale,patternType=None):

        """  """

        for v in self.day:
            for u in v:
                if type(u) == Unit or type(u) == Combination:
                    u.scale(floatScale,patternType)

        return self


    def schedule(self, intYear, intMonth, intDay):

        """  """

        if self.dateBegin == None:

            try:
                dt = date(intYear, intMonth, intDay)
            except ValueError as e:
                print('error: ' + str(e), file=sys.stderr)
                return self

            d_i = datetime.combine(dt,time(0)).astimezone(None)
            
            for d in self.day:
                for t in d:
                    t.setDate(d_i)
                d_i += timedelta(days=1)

            """
            m = len(self)
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

                    if type(self.day[h][i]) == Combination:
                        pass
                    elif self.day[h][i].clock == None:
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

                    if type(self.day[h][i]) == Combination:
                        i += 1
                    elif type(self.day[h][i]) == Unit:
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
                    else:
                        i += 1

                h += 1
            """
            
            self.dateBegin = date(intYear, intMonth, intDay)
            self.dateEnd = self.dateBegin + timedelta(days=(len(self) - 1))

        return self
    

    def stat(self, dictArg):

        """  """

        for v in self.day:
            for u in v:
                if type(u) == Unit or type(u) == Combination:
                    u.stat(dictArg)


    def report(self, dictArg=None):

        """  """

        if dictArg == None:
            dictArg = {}

        self.stat(dictArg)
        #print('info: ' + str(dictArg), file=sys.stderr)

        sum_h = 0.0
        strResult = ''
        for k in sorted(dictArg.keys()):
            # all registered kinds of units
            sum_k = sum(dictArg[k][1])
            if len(dictArg[k][0]) < 1:
                # no distances found
                strResult += "{:4} x {:3} {:7}    {:7.01f} h\n".format(len(dictArg[k][0]), k, ' ', round(sum_k / 3600, 2))
            elif len(dictArg[k][0]) < 3:
                # no statistics required
                strResult += "{:4} x {:3} {:7.01f} {} {:7.01f} h\n".format(len(dictArg[k][0]), k, sum(dictArg[k][0]), config.unit_distance, round(sum_k / 3600, 2))
            else:
                strResult += "{:4} x {:3} {:7.01f} {} {:7.01f} h {:5.01f} /{:5.01f} /{:5.01f}\n".format(len(dictArg[k][0]), k, sum(dictArg[k][0]), config.unit_distance, round(sum_k / 3600, 2), min(dictArg[k][0]), mean(dictArg[k][0]), max(dictArg[k][0]))
            sum_h += sum_k / 3600

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

        return str(self)


    def toHtml(self):

        """  """
        
        strResult = '<section class="{}"'.format(__name__)

        if self.color != None:
            strResult += ' style="background-color: {}"'.format(self.color)

        strResult += '><div class="header">' + self.getTitleXML() + ' (' + str(len(self)) + ', ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '</div>\n'

        strResult += '<ul>' + self.__listDescriptionToHtml__() + '</ul>'

        for v in self.day:
            for u in v:
                strResult += u.toHtml()
            
        strResult += '<pre>' + self.report() + '</pre>'
        
        strResult += '</section>'

        return strResult


    def toCSV(self):

        """  """

        strResult = '\n* ' + self.getTitleStr() + ' (' + str(len(self)) + ', ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n'
        for v in self.day:
            for u in v:
                if type(u) == Unit:
                    strResult += u.toCSV() + '\n'

        return strResult


    def toSVG(self,x,y):

        """  """

        strResult = '<g>'

        strResult += '<line stroke="black" stroke-width=".5" stroke-dasharray="2,10" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(0,y,x+config.diagram_width,y)

        if self.color != None:
            strResult += '<rect fill="{}" x="{}" y="{}" height="{}" width="{}"/>\n'.format(self.color,1,y+1,((config.diagram_bar_height * 2)*len(self))-2,x+config.diagram_width-4)

        strResult += '<text x="{}" y="{}" style="vertical-align:top" text-anchor="right"><tspan x="10" dy="1.5em">{}</tspan><tspan x="10" dy="1.5em">{}</tspan><title>{}</title></text>\n'.format(0,y,self.getTitleXML(), '(' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ') ', (self.getTitleXML() + ' (' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')\n\n' + self.__listDescriptionToString__() + '\n\n' + self.report()))

        if len(self) < 1:
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
                    strResult += u.toSVG(x_i,y)
                    if type(u) == Unit or type(u) == Combination:
                        x_i += u.getDuration().total_seconds() / 3600 * 25 * config.diagram_scale_dist + 5

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
            
        strResult += '<rect opacity=".75" stroke="red" stroke-width=".5" fill="{}" x="{}" y="{}" height="{}" width="{}" rx="2">\n'.format(color, x_i, y, config.diagram_bar_height*2, len(self) * 2)
        strResult += '<title>{}</title>\n'.format(self.getTitleXML() + ' (' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ') ' + self.__listDescriptionToString__())
        strResult += '</rect>'

        # TODO: make config.diagram_height configurable
        config.diagram_height = 40 * (config.diagram_bar_height * 2) + 100

        h = round(self.getDuration().total_seconds() / 60 / l)

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
        strResult += '<title>{}</title>\n'.format(self.getTitleXML() + ' (' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')\n\n' + self.__listDescriptionToString__() + '\n\n' + self.report())
        strResult += '</rect>'

        #strResult += '<text x="{}" y="{}">{}</text>\n'.format(x_i,y,self.getTitleXML())
        strResult += '</g>'

        return strResult


    def toFreemind(self):

        """  """

        strResult = '<node'

        if self.color != None:
            strResult += ' BACKGROUND_COLOR="{}"'.format(self.color)
        elif self.getNumberOfUnits() < 1:
            strResult += ' BACKGROUND_COLOR="{}"'.format('#ffaaaa')
        else:
            strResult += ' FOLDED="{}"'.format('true')

        strResult += ' TEXT="' + self.getTitleXML() + '&#xa;(' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')&#xa;' + self.report().replace('\n','&#xa;') + '">\n'
        strResult += '<font BOLD="false" NAME="Monospaced" SIZE="12"/>'

        strResult += self.__listDescriptionToFreemind__()

        for v in self.day:
            for u in v:
                strResult += u.toFreemind()
            
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

