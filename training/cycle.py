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

from datetime import timedelta, date, datetime, time

from icalendar import Calendar, Event, Alarm

from suntime import Sun

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

        strResult = '\n** ' + super().getTitleStr()
        if type(self.dateBegin) == date:
            strResult += ' (' + str(len(self)) + ', ' + self.dateBegin.strftime("%Y-%m-%d") + ' .. ' + self.dateEnd.strftime("%Y-%m-%d") + ')'
        strResult += '\n\n'

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
                    if type(u) == Combination:
                        c = u.remove(patternType)
                        if c.getNumberOfUnits() > 0:
                            daysNew[i].append(c)
                    elif type(u) == Unit and (u.type == None or re.match(patternType,u.type)):
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
                # override existing
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


    def insert(self,objIndex,objArg,flagReplace=False):

        """  """

        objResult = None

        if objArg == None:
            
            print('error: ' + str(objArg), file=sys.stderr)
            
        elif type(objIndex) == list and len(objIndex) > 0:
            
            for i in objIndex:
                self.insert(i,objArg,flagReplace)
            return []
        
        elif type(objArg) == list and len(objArg) > 0:
            
            for u in objArg:
                self.insert(objIndex,u,flagReplace)
            return []
        
        elif (type(objArg) == Unit or type(objArg) == Combination or type(objArg) == Note) and objIndex > -1 and objIndex < len(self):
            
            objResult = objArg.dup()

            if flagReplace:
                # override existing
                self.day[objIndex] = [objResult]
            else:
                self.day[objIndex].append(objResult)
                
        elif type(objArg) == Cycle and objIndex > -1 and objIndex < len(self) and len(objArg) > 0 and len(objArg) + objIndex <= len(self):

            i = 0
            
            for v in objArg.day:
                
                if flagReplace:
                    # override existing
                    self.day[objIndex + i] = []
                    
                for u in v:
                    self.day[objIndex + i].append(u.dup())
                    
                i += 1

            objResult = self
            
        else:
            print('error: ' + str(objArg), file=sys.stderr)
            
        return objResult


    def insertByDate(self,objArg,flagReplace=False):

        """  """

        objResult = None

        if objArg == None or objArg.dt == None:
            print('error: ' + str(objArg), file=sys.stderr)
        elif type(objArg) == Unit or type(objArg) == Combination or type(objArg) == Note:
            delta = objArg.dt.date() - self.dateBegin
            if delta.days > -1 and objArg.dt.date() <= self.dateEnd:
                objResult = objArg.dup()
                if flagReplace:
                    # override existing
                    self.day[delta.days] = [objResult]
                else:
                    self.day[delta.days].append(objResult)

        return objResult


    def postpone(self,n=1):

        """  """

        if type(n) == int and n > 0 and len(self.day) > n:

            d = self.day[:(len(self.day) - n)]
            for i in range(0,n):
                d.insert(0,[])

            self.day = d
            
        return self


    def stretch(self,n=2):

        """  """

        if type(n) == int and n > 0 and len(self.day) > n:

            d = []
            for i in range(0,len(self.day)):
                d.append(self.day[i])
                for j in range(0,n-1):
                    d.append([])

            self.day = d
            
        return self


    def getCycleByDate(self,objDate=None):

        """  """

        if objDate == None:
            return self.getCycleByDate(datetime.now())
        elif type(objDate) == str:
            return self.getCycleByDate(datetime.fromisoformat(objDate))
        elif type(objDate) == date:
            return self.getCycleByDate(datetime.combine(objDate,time(0)))
        elif type(objDate) == datetime:
            for v in self.day:
                if self.dateBegin <= objDate.date() and objDate.date() <= self.dateEnd:
                    return self

        return None


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

        try:
            self.dateBegin = date(intYear, intMonth, intDay)
        except ValueError as e:
            print('error: ' + str(e), file=sys.stderr)
            return self

        #if config.sun != None:
        #    print('sunrise/sunset: ' + str(config.twilight), file=sys.stderr)

        dt_earliest = None
        dt_latest   = None
        dt_i = datetime.combine(self.dateBegin,time(0)).astimezone(None)

        for d in self.day:

            if config.sun != None:
                # fix 't' according to sunrise/sunset
                dt_earliest = config.sun.get_local_sunrise_time(dt_i) + timedelta(seconds=config.twilight)
                dt_latest   = config.sun.get_local_sunset_time(dt_i)  - timedelta(seconds=config.twilight)

            for t in d:
                t.setDate(dt_i,dt_earliest,dt_latest)

            dt_i += timedelta(days=1)

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
                # no distances found
                strResult += ("{:4} x {:" + str(config.max_length_type) + "} {:7}    {:7.01f} h {:.02f}\n").format(len(dictArg[k][0]),
                                                                                                           k,
                                                                                                           ' ',
                                                                                                           round(sum_k, 2),
                                                                                                           round(sum_k / sum_h, 2))
            elif len(dictArg[k][0]) < 3:
                # no statistics required
                strResult += ("{:4} x {:" + str(config.max_length_type) + "} {:7.01f} {} {:7.01f} h {:.02f}\n").format(len(dictArg[k][0]),
                                                                                                               k,
                                                                                                               sum(dictArg[k][0]),
                                                                                                               config.unit_distance,
                                                                                                               round(sum_k, 2),
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

        strResult += '><div class="header">' + self.getTitleXML() + ' (' + str(len(self)) + ', ' + self.dateBegin.strftime("%Y-%m-%d") + ' .. ' + self.dateEnd.strftime("%Y-%m-%d") + ')' + '</div>\n'

        strResult += '<ul>' + self.__listDescriptionToHtml__() + '</ul>'

        for v in self.day:
            for u in v:
                strResult += u.toHtml()
            
        strResult += '<pre>' + self.report() + '</pre>'
        
        strResult += '</section>'

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

        strResult = '\n* ' + self.getTitleStr() + ' (' + str(len(self)) + ', ' + self.dateBegin.strftime("%Y-%m-%d") + ' .. ' + self.dateEnd.strftime("%Y-%m-%d") + ')' + '\n'
        for v in self.day:
            for u in v:
                if type(u) == Unit:
                    strResult += u.toCSV() + '\n'

        return strResult


    def toSqlite(self):

        """  """

        strResult = ''
        for v in self.day:
            for u in v:
                if type(u) == Unit:
                    strResult += u.toSqlite()
            
        return strResult


    def toSVG(self, x = config.diagram_offset, y=20):

        """  """

        strResult = '<g>'

        strResult += '<line stroke="black" stroke-width=".5" stroke-dasharray="2,10" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(0,y,x+config.diagram_width,y)

        if self.color != None:
            strResult += '<rect fill="{}" x="{}" y="{}" height="{}" width="{}"/>\n'.format(self.color,1,y+1,((config.diagram_bar_height * 2)*len(self))-2,x+config.diagram_width-4)

        strResult += '<text x="{}" y="{}" style="vertical-align:top" text-anchor="right"><tspan x="10" dy="1.5em">{}</tspan><tspan x="10" dy="1.5em">{}</tspan><title>{}</title></text>\n'.format(0,y,self.getTitleXML(), '(' + self.dateBegin.strftime("%Y-%m-%d") + ' .. ' + self.dateEnd.strftime("%Y-%m-%d") + ') ', (self.getTitleXML() + ' (' + self.dateBegin.strftime("%Y-%m-%d") + ' .. ' + self.dateEnd.strftime("%Y-%m-%d") + ')\n\n' + self.__listDescriptionToString__() + '\n\n' + self.report()))

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
        strResult += '<title>{}</title>\n'.format(self.getTitleXML() + ' (' + self.dateBegin.strftime("%Y-%m-%d") + ' .. ' + self.dateEnd.strftime("%Y-%m-%d") + ') ' + self.__listDescriptionToString__())
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
        strResult += '<title>{}</title>\n'.format(self.getTitleXML() + ' (' + self.dateBegin.strftime("%Y-%m-%d") + ' .. ' + self.dateEnd.strftime("%Y-%m-%d") + ')\n\n' + self.__listDescriptionToString__() + '\n\n' + self.report())
        strResult += '</rect>'

        #strResult += '<text x="{}" y="{}">{}</text>\n'.format(x_i,y,self.getTitleXML())
        strResult += '</g>'

        return strResult


    def toSVGGanttChart(self):

        """ Gantt chart of this cycle """

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


    def toFreemindNode(self):

        """  """

        strResult = '<node'

        if self.color != None:
            strResult += ' BACKGROUND_COLOR="{}"'.format(self.color)
        elif self.getNumberOfUnits() < 1:
            strResult += ' BACKGROUND_COLOR="{}"'.format('#ffaaaa')
        else:
            strResult += ' FOLDED="{}"'.format('true')

        strResult += ' TEXT="' + self.getTitleXML() + '&#xa;(' + self.dateBegin.strftime("%Y-%m-%d") + ' .. ' + self.dateEnd.strftime("%Y-%m-%d") + ')&#xa;' + self.report().replace('\n','&#xa;') + '">\n'
        strResult += '<font BOLD="false" NAME="Monospaced" SIZE="12"/>'

        strResult += self.__listDescriptionToFreemind__()

        d_i = self.dateBegin
        for v in self.day:
            strResult += '<node TEXT="' + d_i.strftime("%Y-%m-%d %a") + '"'
            if d_i.isoweekday() == 6 or d_i.isoweekday() == 7:
                strResult += ' BACKGROUND_COLOR="{}"'.format('#eeeeee')
            strResult += '>'
            for u in v:
                strResult += u.toFreemindNode()
            strResult += '</node>\n'
            d_i += timedelta(days=1)
            
        strResult += '</node>\n'

        return strResult


    def toFreeMind(self):

        """  """

        strResult = '<?xml version="1.0" encoding="UTF-8"?><map>\n'
        strResult += self.toFreemindNode()
        strResult += '</map>\n'

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


    def toVCalendar(self):

        """  """

        cal = Calendar()
        cal.add('prodid', '-//{title}//  //'.format(title=self.getTitleStr()))
        cal.add('version', '2.0')
        self.to_ical(cal)
        return cal.to_ical()


