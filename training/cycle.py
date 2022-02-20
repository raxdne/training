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

from datetime import timedelta, date, datetime, time

from icalendar import Calendar, Event, Alarm

from description import Description

from title import Title

from unit import Unit

import training as config

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

        self.child = []
        for i in range(0,int(intArg)):
            self.child.append([])

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

        for v in self.child:
            for u in v:
                u.setDistStr(None)

        return self


    def resetUnits(self,patternType=None):

        """  """

        if patternType == None:
            for v in self.child:
                del v[0:]
        else:
            for v in self.child:
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

        return len(self.child)


    def insert(self,intIndex,objUnit):

        """  """

        objResult = None

        if objUnit != None:
            objResult = objUnit.dup()
            self.child[intIndex].append(objResult)

        return objResult


    def insertByDate(self,objUnit,flagReplace=False):

        """  """

        objResult = None

        if objUnit != None and objUnit.date != None:
            delta = objUnit.date - self.dateBegin
            if delta.days > -1 and objUnit.date <= self.dateEnd:
                objResult = objUnit.dup()
                if flagReplace:
                    # delete exisiting
                    self.child[delta.days] = [objResult]
                else:
                    self.child[delta.days].append(objResult)

        return objResult


    def insertDescriptionStr(self,intIndex,strArg):

        """  """

        if strArg == None or strArg == '':
            pass
        elif len(self.child) > intIndex and len(self.child[intIndex]) > 0:
            self.child[intIndex][len(self.child[intIndex]) - 1].appendDescription(strArg)


    def getPeriod(self):

        """  """

        return len(self.child)


    def getNumberOfUnits(self):

        """  """

        intResult = 0
        for v in self.child:
            for u in v:
                if u.type != None and len(u.type) > 0:
                    intResult += 1
                elif u.duration != None and u.duration.total_seconds() > 59:
                    intResult += 1

        return intResult


    def getDurationOfUnits(self):

        """ in minutes """

        intResult = 0
        for v in self.child:
            for u in v:
                if u.type != None and len(u.type) > 0 and u.duration != None and u.duration.total_seconds() > 59:
                    intResult += u.duration.total_seconds()

        return intResult / 60


    def getTypeOfUnits(self,arrArg=None):

        """  """

        if arrArg == None:
            arrArg = []

        for v in self.child:
            for u in v:
                if u.type != None and len(u.type) > 0:
                    if u.type in arrArg:
                        pass
                    else:
                        arrArg.append(u.type)

        return arrArg


    def scale(self,floatScale,patternType=None):

        """  """

        for v in self.child:
            for u in v:
                u.scale(floatScale,patternType)

        return self


    def schedule(self, intYear, intMonth, intDay):

        """  """

        if self.dateBegin == None:
            try:
                d = date(intYear, intMonth, intDay)
            except:
                print('ignoring: invalid date {}-{}-{}'.format(intYear, intMonth, intDay), file=sys.stderr)
                return self

            for v in self.child:
                o = self.child.index(v)
                for u in v:
                    u.setDate(d + timedelta(days=o))

            self.dateBegin = date(intYear, intMonth, intDay)
            self.dateEnd = self.dateBegin + timedelta(days=(self.getPeriod() - 1))

        return self
    

    def stat(self, arrArg):

        """  """

        for v in self.child:
            for u in v:
                if u.dist == None or u.type == None or len(u.type) < 1:
                    pass
                else:
                    arrArg[u.date.month - 1][u.type] += u.dist


    def report(self, arrArg=None):

        """  """

        if arrArg == None:
            arrArg = {}

        strResult = ''

        for v in self.child:
            for u in v:
                if u.type != None and len(u.type) > 0 and u.duration != None:
                    if u.type in arrArg:
                        if u.dist != None:
                            if arrArg[u.type][0] == None:
                                arrArg[u.type][0] = u.dist
                            else:
                                arrArg[u.type][0] += u.dist
                        arrArg[u.type][1] += 1
                        arrArg[u.type][2] += u.duration.total_seconds()
                    else:
                        arrArg[u.type] = []
                        if u.dist != None:
                            arrArg[u.type].append(u.dist)
                        else:
                            arrArg[u.type].append(None)

                        arrArg[u.type].append(1)
                        arrArg[u.type].append(u.duration.total_seconds())

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
            strResult += "{:4} h     in {} Days = {:4.01f} h/Week\n".format(round(sum_h), p, sum_h/p * 7.0)

        return strResult


    def dup(self):

        """  """

        return copy.deepcopy(self)


    def toString(self):

        """  """

        strResult = '\n** ' + self.getTitleStr() + ' (' + str(self.getPeriod()) + ', ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n\n'
        for v in self.child:
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
        
        for v in self.child:
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
        for v in self.child:
            for u in v:
                strResult += u.toCSV() + '\n'

        return strResult


    def toSVG(self,x,y):

        """  """

        strResult = '<g>'

        strResult += '<line stroke="black" stroke-width=".5" stroke-dasharray="2,10" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(0,y,x+config.diagram_width,y)

        if self.color != None:
            strResult += '<rect fill="{}" x="{}" y="{}" height="{}" width="{}"/>\n'.format(self.color,1,y+1,((config.diagram_bar_height * 2)*len(self.child))-2,x+config.diagram_width-4)

        strResult += '<text x="{}" y="{}" style="vertical-align:top" text-anchor="right"><tspan x="10" dy="1.5em">{}</tspan><tspan x="10" dy="1.5em">{}</tspan><title>{}</title></text>\n'.format(0,y,self.getTitleStr(), '(' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ') ', self.__listDescriptionToString__())

        if len(self.child) < 1:
            pass
        else:
            y += config.diagram_bar_height / 2
            t = date.today()
            d = self.dateBegin
            for v in self.child:
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
                    if u.type != None and u.duration != None:
                        strResult += u.toSVG(x_i,y)
                        x_i += u.duration.total_seconds() / 3600 * 25 * config.diagram_scale_dist

                for u in v:
                    # all remarks after
                    if u.type == None:
                        strResult += u.toSVG(x_i,y)
                        x_i += len(u.toString()) * config.font_size

                y += config.diagram_bar_height * 2

        strResult += '</g>'

        return strResult


    def toSVGGantt(self,dateBase,y=0):

        """  """
    
        try:
            l = self.dateEnd - self.dateBegin
            x_i = (self.dateBegin - dateBase).days * 2
        except:
            return ''
        
        strResult = '<g>'

        if self.color == None:
            color = '#ffaaaa'
        else:
            color = self.color
            
        strResult += '<rect opacity=".75" stroke="red" stroke-width=".5" fill="{}" x="{}" y="{}" height="{}" width="{}" rx="2">\n'.format(color, x_i, y, config.diagram_bar_height*2, (l.days + 1) * 2)
        strResult += '<title>{}</title>\n'.format(self.getTitleStr() + ' (' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ') ' + self.__listDescriptionToString__())
        strResult += '</rect>'

        # TODO: make training.config.diagram_height configurable
        config.diagram_height = 40 * (config.diagram_bar_height * 2) + 100

        h = round(self.getDurationOfUnits() / (l.days + 1))

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
            
        strResult += '<rect opacity=".75" stroke="{}" stroke-width=".5" fill="{}" x="{}" y="{}" height="{}" width="{}">\n'.format(scolor, color, x_i + 1, config.diagram_height - h - 10, h, (l.days + 1) * 2 - 2)
        strResult += '<title>{}</title>\n'.format(self.getTitleStr() + ' (' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ') ' + self.__listDescriptionToString__() + ' ' + str(h) + ' min/d' )
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

        for v in self.child:
            for u in v:
                strResult += u.toXML()
        strResult += '</node>\n'

        return strResult


    def toiCalString(self):

        """  """

        e = self.dateEnd + timedelta(days=1)

        if self.getNumberOfUnits() < 1:
            strResult = "BEGIN:VEVENT\nSUMMARY:Period {title}\nDTSTART;{y:04}{m:02}{d:02}\nDTEND;{ye:04}{me:02}{de:02}\nDTSTAMP;{y:04}{m:02}{d:02}\nEND:VEVENT\n".format(title=self.getTitleStr(), y=self.dateBegin.year, m=self.dateBegin.month, d=self.dateBegin.day, ye=e.year, me=e.month, de=e.day)
        else:
            strResult = ''
            for v in self.child:
                for u in v:
                    strResult += u.toiCalString()

        return strResult


    def to_ical(self,cal):

        """  """

        event = Event()
        event.add('summary', 'Cycle: {}'.format(self.getTitleStr()))
        event.add('dtstart', self.dateBegin)
        event.add('dtend', self.dateEnd + timedelta(days=1))
        event.add('dtstamp', datetime.now().astimezone(None))
        cal.add_component(event)

        for v in self.child:
            for u in v:
                u.to_ical(cal)


if __name__ == "__main__":
    
    print('Module Test:\n')
    
    c = Cycle('C1',2*7)

    c.insert(1,Unit('18:00;3.5;RB;25:00'))
    c.insert(3,Unit('18:00;3.5;RB;25:00'))
    c.insert(4,Unit(';FB;25:00'))
    c.insert(5,Unit(';FB;25:00'))
    c.insert(6,Unit('08:00;30;BB;02:00:00'))
    c.insert(8,Unit(';FB;25:00'))
    c.insert(10,Unit(';FB;25:00'))
    c.insert(13,Unit('08:00;30;BB;02:00:00'))

    c.schedule(2022,3,1)
    c.schedule(2023,3,1)
    
    print(c.toString())

    print(c.toSVG(0,0))
