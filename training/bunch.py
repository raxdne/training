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

from pathlib import Path

import math

import copy

import re

import os

from statistics import mean

from datetime import timedelta, date, datetime, time

from icalendar import Calendar, Event, Alarm

import numpy as np

from suntime import Sun

from training import config as config
from training.tcontainer import TContainer

from training.titem import TItem
from training.note import Note
from training.unit import Unit
from training.pause import Pause
from training.combination import Combination
from training.exerciseset import ExerciseSet
from training.cycle import Cycle
#from training.plot import Plot

#
#
#

# REQ: compact layout to _display_ all items of n days (blocks?) in one table row, if self.fPlan

# REQ: items of n days _planned_ as building blocks (first day of Cycle), if self.fPlan ??


class Bunch(TContainer):

    """ block-oriented alternative of Cycle() """

    def __init__(self,strArg=None,intArg=7):

        """  """

        super().__init__(strArg,intArg)


    def __str__(self):

        strResult = super().__str__()

        for v in self.child:
            strResult += f'{v[0]} x {v[1]}\n'

        return strResult + '\n\n'


    def resetDistances(self):

        """  """

        super().resetDistances()

        return self


    def getLength(self):

        """ return length of cycle """

        return self.periodInt


    def getNumberOfUnits(self, dt0=None, dt1=None):

        """  """

        intResult = 0
        for v in self.child:
            u = v[1]
            if u.dt is not None and ((dt0 is not None and u.dt.date() < dt0) or (dt1 is not None and dt1 < u.dt.date())):
                # u is out of interval
                pass 
            elif type(u) is Combination:
                intResult += u.getNumberOfUnits(dt0,dt1)
            elif type(u) is Unit and u.isCountable():
                intResult += v[0]

        return intResult


    def getDuration(self, skipType=None):

        """ return a timedelta """

        # TODO: use self.data

        if skipType is None:
            skipType = self.skipType

        intResult = 0
        for v in self.child:
            u = v[1]
            if (type(u) is Unit and u.isCountable()) or type(u) is Combination:
                intResult += v[0] * u.getDuration(skipType).total_seconds()

        return timedelta(seconds=intResult)


    def scale(self,floatScale,patternType=None):

        """ returns a scaled copy of self """

        r = self.dup()
        if floatScale > 0.01 and abs(floatScale - 1.0) > 0.01:
            for i in range(len(r.child)):
                if type(r.child[i][1]) is Unit or type(r.child[i][1]) is ExerciseSet or type(r.child[i][1]) is Combination:
                    r.child[i] = (r.child[i][0], r.child[i][1].scale(floatScale,patternType))

        r.summary.clear()

        return r


    def stat(self, dt0=None, dt1=None, skipType=None):

        """ stat all descendant data to self.data and returns it as a nested list  """

        if skipType is None:
            skipType = self.skipType

        self.data.clear()

        for v in self.child:
            u = v[1]
            if (type(u) is Unit and u.isCountable()) or type(u) is Combination:
                self.data.extend(v[0] * u.stat(skipType))

        return self.data


    def updateValues(self,dictArg=None):

        """  """

        if dictArg is not None:
            self.setVDefaults(dictArg)

        for v in self.child:
            v[1].updateValues(dictArg)

        if False:
            for d in c:
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


    def append(self, objArg=None):

        """  """

        self.data.clear()
        self.summary.clear()

        if objArg is None:
            print('error: empty period initialization', file=sys.stderr)
        elif type(objArg) is str and objArg:
            return self.append([objArg])
        elif type(objArg) is tuple:
            self.child.extend([objArg])
        elif type(objArg) is list and type(objArg[0]) is tuple:
            self.child.extend(objArg)
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


    def cut(self, d0, d1):

        """  """

        return self.cutBefore(d0).cutAfter(d1)


    def cutBefore(self,d):

        """  """

        assert type(d) is date

        if self.dateBegin < d and d <= self.dateEnd:
            for i in range(len(self.child)):
                if isinstance(self.child[i],TContainer):
                    if d == self.child[i].dateBegin:
                        del self.child[:i]
                        break
                    elif self.child[i].dateBegin < d and d <= self.child[i].dateEnd:
                        self.child[i].cutBefore(d)
                        del self.child[:i]
                        break

            #for i in range(len(self.tag)):
            #    if d <= self.tag[i].dateBegin or self.tag[i].dateEnd <= d:
            #        del self.tag[i]
            #        i -= 1

            self.setPeriod((self.dateEnd - d).days + 1)
            self.schedule(d)
            self.data.clear()
            self.summary.clear()

        return self


    def cutAfter(self,d):

        """  """

        assert type(d) is date

        if self.dateBegin <= d and d < self.dateEnd:
            for i in range(len(self.child)):
                if isinstance(self.child[i],TContainer):
                    if d == self.child[i].dateEnd:
                        del self.child[i+1:]
                        break
                    elif self.child[i].dateBegin <= d and d < self.child[i].dateEnd:
                        self.child[i].cutAfter(d)
                        del self.child[i+1:]
                        break

            self.setPeriod((d - self.dateBegin).days + 1)
            self.schedule(self.dateBegin)
            self.data.clear()
            self.summary.clear()

        return self


    def fill(self,objArg,floatProgression=1.0):

        """  """

        flagReplace=False
        objResult = self

        if objArg is None:
            print('error: undefined object ' + str(objArg), file=sys.stderr)
        elif type(objArg) is list and objArg:
            for u in objArg:
                self.insert(u,flagReplace)
        elif isinstance(objArg,TContainer) or type(objArg) is Unit or type(objArg) is Combination:
            for c in self.child: # TODO:
                if isinstance(c,TContainer):
                    c.fill(objArg,floatProgression)
        else:
            print(f'error: filling {type(objArg)} of {len(self.child)} {objArg}', file=sys.stderr)

        return objResult


    def toHtmlTable(self):

        """  """

        strResult = f'<section {config.getClass(__name__)} id="{str(id(self))}"'

        if self.color is not None:
            strResult += ' style="background-color: {}"'.format(self.color)

        strResult += '><div class="header" ondblclick="removeDetails(this)">' + self.getTitleXML() + ' ' + self.getDateString() + '</div>\n'

        strResult += self.getDescriptionHTML()

        if self.getNumberOfUnits() > 0:
            strResult += f'<pre {config.getClass(__name__)}>' + self.report() + '</pre>'
            
        m = self.getMarkers()
        if len(m) > 0:
            strResult += '<p>Marked Units (Peaks)</p>'
            strResult += '<ol>'
            for u in m:
                strResult += f'<li>{u}</li>'
            strResult += '</ol>'

        if False and self.fPlot:
            strResult += '<div style="text-align: center;margin: 0px;">'
            #strResult += self.plotAccumulationDuration()
            #strResult += self.plotAccumulation()
            #strResult += self.plotHist()
            #strResult += self.plotTimeDist()
            #strResult += self.toSVGGanttChart()
            strResult += '</div>'
            strResult += self.toSVGDiagram()
        else:
            strResult += '<table>\n'

            strResult += '<colgroup><col span="1" style="width: 10%;"><col span="1" style="width: 90%;"></colgroup>\n'

            strResult += '<tbody>'
            dt_i = datetime.combine(self.dateBegin,time(0)).astimezone(None)

            # REQ: compact layout to _display_ all items of n days (blocks?) in one table row, if self.fPlan

            # REQ: items of n days _planned_ as building blocks (first day of Cycle), if self.fPlan ??

            for v in self.child: # TODO:
                strResult += '<tr>'
                strResult += f'<td>{v[0]} x </td>'
                strResult += '<td>' + v[1].toHtmlTable() + '</td>'
                strResult += '</tr>'

            strResult += '</tbody></table>'

        strResult += '</section>'

        return strResult


    def toCSV(self):

        """  """

        strResult = '{};;;;Cycle "{}" {}\n'.format(self.dateBegin.strftime("%Y-%m-%d"), self.getTitleString(), self.getDateString())
        for v in self.child:
            u = v[1]
            strResult += u.toCSV()
        strResult += '\n'

        return strResult


    def toSqlite(self):

        """  """

        strResult = ''
        for v in self.child:
            u = v[1]
            if type(u) is Unit:
                strResult += u.toSqlite()

        return strResult


    def toSVGGanttMarker(self,dateBase):

        """  """

        strResult = ''

        if self.child:
            strResult += '<g>'
            for v in self.child:
                u = v[1]
                if u.isMarked():
                    x_i = (u.dt.date() - dateBase).days * 2
                    strResult += '<line stroke="red" stroke-width="1" x1="{}" y1="{}" x2="{}" y2="{}">\n'.format(x_i, 0, x_i, config.diagram_width)
                    strResult += f'<title>{u}</title>\n'
                    strResult += '</line>'
            strResult += '</g>'

        return strResult


    def toSVG(self, x = config.diagram_offset, y=0):

        """ returns SVG code for Bunch 'self' in a vertical Timeline """

        strResult = '<g>'

        if self.color is not None:
            strResult += '<rect fill="{}" opacity=".5" x="{}" y="{}" height="{}" width="{}"/>\n'.format(self.color,1,y+1,((config.diagram_bar_height * 2)*len(self.child))-2,x+config.diagram_width-4)

        strResult += '<text x="{}" y="{}" style="vertical-align:top" text-anchor="right"><tspan x="10" dy="1.5em">{}</tspan><tspan x="10" dy="1.5em">{}</tspan><title>{}</title></text>\n'.format(0,y,self.getTitleXML(), self.getDateString(), (self.getTitleXML() + self.getDateString() + '\n\n' + self.getDescriptionString() + '\n\n' + self.report()))

        strResult += '</g>'

        return strResult


    def toSVGGanttChart(self):

        """ Gantt chart of this Bunch (horizontal timeline) """

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

            strResult += '<line stroke-dasharray="8" stroke="{}" stroke-width="1" opacity="0.5" x1="{}" y1="{}" x2="{}" y2="{}">\n'.format(color,w, 0, w, diagram_height)
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

        strResult += self.toSVGGanttBar(d_0)
        
        # TODO: add unit marker if u.isMarked()

        strResult += '</g>'
        strResult += '</svg>\n'

        return strResult


    def toSVGGanttBar(self,dateBase,y=0):

        """ returns SVG string of vertical and horizontal bars in Gantt Chart """

        # TODO: make config.diagram_height configurable
        config.diagram_height = 40 * (config.diagram_bar_height * 2) + 100

        x_i = (self.dateBegin - dateBase).days * 2

        strResult = '<g>'

        # horizontal bar

        if self.color is not None:
            color = self.color
        else:
            color = '#ffaaaa'

        strResult += '<a href="#{}">'.format(str(id(self)))
        strResult += '<rect opacity=".75" stroke="red" stroke-width=".5" fill="{}" x="{}" y="{}" height="{}" width="{}" rx="2">\n'.format(color, x_i, y, config.diagram_bar_height*2, len(self) * 2)
        strResult += '<title>{}</title>\n'.format(self.getTitleXML() + self.getDateString() + ' ' + self.getDescriptionString())
        strResult += '</rect>'
        strResult += '</a>'

        # vertical bar

        l = (self.dateEnd - self.dateBegin).days + 1
        h = round(self.getDuration().total_seconds() / 60 / l)

        if self.color is not None:
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

        strResult += '<a href="#{}">'.format(str(id(self)))
        strResult += '<rect opacity=".75" stroke="{}" stroke-width=".5" fill="{}" x="{}" y="{}" height="{}" width="{}">\n'.format(scolor, color, x_i + 1, config.diagram_height - h - 10, h, l * 2 - 2)
        strResult += '<title>{}</title>\n'.format(self.getTitleXML() + self.getDateString() + '\n\n' + self.getDescriptionString() + '\n\n' + self.report())
        strResult += '</rect>'
        strResult += '</a>'

        strResult += '</g>'

        return strResult


    def toFreemindNode(self):

        """  """

        strResult = '<node'

        if self.color is not None:
            strResult += ' BACKGROUND_COLOR="{}"'.format(self.color)
        elif self.getNumberOfUnits() < 1:
            strResult += ' BACKGROUND_COLOR="{}"'.format('#ffaaaa')
        else:
            strResult += ' FOLDED="{}"'.format('true')

        strResult += ' LOCALIZED_STYLE_REF="default" TEXT="' + self.getTitleXML() + ' ' + self.getDateString() + '&#xa;' + self.report().replace('\n','&#xa;') + '">\n'
        #strResult += '<font BOLD="false" NAME="Monospaced" SIZE="12"/>'

        strResult += self.getDescriptionFreemind()

        d_i = self.dateBegin
        for v in self.child:
            u = v[1]
            strResult += '<node TEXT="' + d_i.strftime("%Y-%m-%d %a") + '"'
            if d_i.isoweekday() == 6 or d_i.isoweekday() == 7:
                strResult += ' BACKGROUND_COLOR="{}"'.format('#eeeeee')
            strResult += '>'
            for i in range(v[9]):
                strResult += u.toFreemindNode()
            strResult += '</node>\n'
            d_i += timedelta(days=1)

        strResult += '</node>\n'

        return strResult


    def to_ical(self,cal):

        """  """

        return self


    def toVCalendar(self):

        """  """

        cal = Calendar()
        cal.add('prodid', '-//{title}//  //'.format(title=self.getTitleString()))
        cal.add('version', '2.0')
        #self.to_ical(cal)
        return cal.to_ical()


if __name__ == '__main__':

    print('Module Test: ' + __file__ + '\n')
    
    t = Bunch('TEST',3*7).schedule(2023,12,8)

    t.append((12,Unit(';30;BB;01:10:00')))
    t.append((7,Unit(';10;BR;01:00:00')))
    t.appendDescription('Running Blocks')
    t.scale(1.25)
    
    print(t)
    print(t.report())
