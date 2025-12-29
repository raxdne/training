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

import re

import copy

from datetime import timedelta, date, datetime, time, timezone

from icalendar import Calendar, Event, Alarm

from training import config as config
from training.duration import Duration
from training.note import Note

#
#
#

class Unit(Note):

    """ class for training units """

    def __init__(self,strArg=None):

        """  """

        super().__init__()
        
        self.dist = None
        self.type = None
        self.duration = None
        
        self.setDuration(0)

        self.parse(strArg)


    def __str__(self):

        """  """

        if self.type is None and self.dist is None and self.dt is None:
            strResult = '-'
        elif self.type is None:
            if self.dt is None or self.dt.time() == time(0):
                strResult = f'{self.dt.strftime("%Y-%m-%d")} {self.getDurationString()}'
            else:
                strResult = f'{self.dt.strftime("%Y-%m-%d %H:%M:%S")} {self.getDurationString()}'
        elif self.dist is None:
            if self.dt is None:
                strResult = f'{self.type} {self.getDurationString()}'
            elif self.dt.time() == time(0):
                strResult = f'{self.dt.strftime("%Y-%m-%d")} {self.type} {self.getDurationString()}'
            else:
                strResult = f'{self.dt.strftime("%Y-%m-%d %H:%M:%S")} {self.type} {self.getDurationString()}'
        elif self.dt is None:
            strResult = f'{self.getDistString():>7} {self.type} {self.getDurationString()}'
        elif self.dt.time() == time(0):
            strResult = f'{self.dt.strftime("%Y-%m-%d")} {self.getDistString():>7} {self.type} {self.getDurationString()}'
        else:
            strResult = f'{self.dt.strftime("%Y-%m-%d %H:%M:%S")} {self.getDistString():>7} {self.type} {self.getDurationString()}'

        if self.isMarked():
            strResult += '*'
    
        return strResult


    def toStringShort(self):

        """  """
    
        strResult = ''

        if self.dist is not None:
            strResult += self.getDistString() + ' '
        
        if self.type is not None:
            strResult += self.type + ' '

        strResult += self.getDurationString()

        return strResult


    def setDate(self,dtArg=None,dt_0=None,dt_1=None):

        """ fix 'dt' according to sunrise dt_0 or sunset dt_1 """

        #print('setDate(' + dtArg.isoformat() + ' '  + dt_0.isoformat() + ' ' + dt_1.isoformat() + ') = ' + self.dt.isoformat() , file=sys.stderr)

        if dtArg is None:
            
            self.dt = None
            return self.dt
        
        elif type(dtArg) is date:
            
            return self.setDate(datetime.combine(dtArg,time(0)).astimezone(None),dt_0,dt_1)

        elif type(dtArg) is datetime:

            if self.tPlan is None:
                self.dt = dtArg
            elif type(self.tPlan) is str and self.tPlan == 'sunrise' and dt_0 is not None:
                # shift start time after twilight
                self.dt = dt_0
                # adjust to 15min steps
                self.dt -= timedelta(minutes=(self.dt.minute % 15))
            elif type(self.tPlan) is str and self.tPlan == 'sunset' and dt_1 is not None:
                # shift end time before twilight
                self.dt = dt_1 - self.duration
                self.dt -= timedelta(minutes=(self.dt.minute % 15))
            elif type(self.tPlan) is time:
                self.dt = datetime.combine(dtArg.date(),self.tPlan).astimezone(None)
            else:
                #self.dt = datetime.combine(dtArg.date(),time(0)).astimezone(None)
                self.dt = dtArg
        
        else:
            print('error: date type unknown', file=sys.stderr)
                
        return self.dt + self.duration
        

    def setTypeStr(self,strArg):

        """  """

        if strArg is None or strArg == '':
            return False
        elif config.max_length_type > 0 and config.max_length_type < 32:
            self.type = strArg[0:config.max_length_type]
        else:
            self.type = strArg

        return True


    def setDistStr(self,strArg=None):

        """  """

        if strArg is None or not strArg:
            self.dist = None
        else:
            try:
                self.dist = float(strArg.replace(',','.'))
                if self.dist < 0.001:
                    self.dist = None
            except ValueError:
                self.dist = None

        return (self.dist is not None and self.dist > 0.1)


    def getDistString(self):

        """  """

        strResult = ''
        
        if self.dist is None:
            pass
        elif self.dist < 1.0:
             strResult = '{:.02f} {}'.format(self.dist, config.unit_distance)
        elif self.dist < 10.0:
             strResult = '{:.1f} {}'.format(self.dist, config.unit_distance)
        else:
             strResult = '{:.0f} {}'.format(self.dist, config.unit_distance)

        return strResult


    def setDuration(self,intArg=None):

        """  """

        if intArg is None or intArg == 0:
            self.duration = Duration(0)
        else:
            self.duration = Duration(intArg)

        return (self.duration is not None and self.duration != Duration(0))


    def getDuration(self):

        """  """
        
        if self.duration is None:
            self.setDuration()

        if self.type is not None and self.type:
            return self.duration

        return Duration(0)


    def getDurationString(self):

        """  """
        
        return self.getDuration().toString()


    def updateValues(self,dictArg=None):

        """  """

        if dictArg is not None:
            if self.type is not None and self.type in dictArg and dictArg[self.type] > 1.0 and self.duration is not None and self.duration > Duration(0):
                if self.dist is None or self.dist < 0.1:
                    # there is a defined default velocity
                    self.dist = dictArg[self.type] * (self.duration.total_seconds() / 3600)
                    #print('info updating distance: ' + str(self), file=sys.stderr)
            elif self.type is not None and self.type in dictArg and dictArg[self.type] > 1.0 and self.dist is not None and self.dist > 0.1:
                if self.duration is None or self.duration < Duration(1):
                    # there is a defined default velocity
                    self.duration = Duration(int(self.dist / dictArg[self.type] * 60))
                    #print('info updating duration: ' + str(self), file=sys.stderr)

        return self


    def match(self,patternType=None):
                            
       return (self.type is None or patternType is None or re.match(patternType,self.type))


    def isCountable(self):

        """  """

        return ((type(self.type) is str and self.type) and (type(self.dist) is float and self.dist > 0.0) and self.getDuration().total_seconds() > 0)


    def scale(self,floatScale,patternType=None):

        """  """

        if floatScale > 0.01 and  abs(floatScale - 1.0) > 0.01 and (patternType is None or self.type is None or re.match(patternType,self.type)):

            if self.dist is not None:
                if self.dist < 20.0:
                    self.dist *= floatScale
                else:
                    # round distance to 5.0
                    self.dist = round(self.dist * floatScale / 5.0) * 5.0

            if self.duration is not None:
                self.duration = self.duration.scale(floatScale)

        return self


    def parse(self,objArg):

        """  """
        
        if objArg is None or not objArg:
            return False
        elif type(objArg) is str:
            entry = objArg.split(';')
            # TODO: test elements of entry
            if len(entry) == 1:
                # type only
                entry.insert(0,'')
                entry.insert(0,'')
                entry.append('')
                entry.append('')
            elif len(entry) == 2:
                # type + time only
                entry.insert(0,'')
                entry.insert(0,'')
                entry.append('')
            elif len(entry) == 3:
                # dist + type + time
                entry.insert(0,'')
            return self.parse(entry)
        elif type(objArg) is list and len(objArg) > 3:

            if self.setTypeStr(objArg[2]):
                if self.setDuration(objArg[3]):
                    if self.setDistStr(objArg[1]):
                        pass
                    else:
                        self.setDistStr()
                elif self.setDistStr(objArg[1]):
                    self.setDuration()

                self.setDateStr(objArg[0])
                self.appendDescription(objArg[4:])
                return True
            else:
                return False
        else:
            return False


    def stat(self):

        """  """

        listResult = []
        
        if self.type is None or not self.type:
            #print('error: ' + 'no type', file=sys.stderr)
            pass
        elif self.dist is None or self.dist < 0.001:
            #print('error: ' + 'no dist', file=sys.stderr)
            listResult = [[0, 0.0, self.getDuration().total_seconds() / 60, self.type]]
        elif self.duration is None:
            #print('error: ' + 'no duration', file=sys.stderr)
            listResult = [[0, self.dist, 0.0, self.type]]
        elif self.dt is None:
            listResult = [[0, self.dist, self.getDuration().total_seconds() / 60, self.type]]
        else:
            listResult = [[self.dt.toordinal(), self.dist, self.getDuration().total_seconds() / 60, self.type]]

        return listResult


    def getColor(self):

        """  """
        
        strResult = ''
        
        if self.color is not None:
            strResult = self.color
        elif self.type is None or not self.type:
            strResult = '#cccccc'
        elif self.type in config.colors:
            strResult = config.colors[self.type]
        elif self.type[0] in config.colors:
            strResult = config.colors[self.type[0]]

        return strResult

            
    def getSpeedStr(self):

        """  """

        strResult = ''
        if self.dist is None or self.duration is None:
            pass
        else:
            s = float(self.getDuration().total_seconds())
            if s < 1:
                pass
            else:
                min, sec = divmod(s / self.dist, 60)
                strResult += f'{min:0.0f}:{sec:02.0f} min/{config.unit_distance} '
                strResult += f'{self.dist / (s / 3600):.0f} {config.unit_distance}/h '

        return strResult


    def toCSV(self):

        """  """

        if self.dt is None:
            strResult = ''
        else:
            if self.type is None:
                strResult = '{date};;;'.format(date=self.dt.strftime("%Y-%m-%d"))
            elif self.dist is None:
                strResult = '{date};;{type};{duration}'.format(date=self.dt.strftime("%Y-%m-%d"), type=self.type, duration=self.getDuration())
            else:
                strResult = '{date};{dist:.1f};{type};{duration}'.format(date=self.dt.strftime("%Y-%m-%d"), dist=self.dist, type=self.type, duration=self.getDuration())

            strResult += ';' + self.getDescriptionString() + '\n'

        return strResult


    def toSqlite(self):

        """  """

        if self.dt is None or self.type is None or self.dist is None:
            # not significant for reports
            strResult = ''
        else:
            strResult = "INSERT INTO 'units' VALUES ('{date}',{dist:.1f},'{type}','{duration}','{description}');\n".format(date=self.dt.strftime("%Y-%m-%d"), dist=self.dist, type=self.type, duration=self.getDuration(), description=self.getDescriptionString())

        return strResult


    def toHtmlTable(self):

        """  """

        return f'<div style="background-color: {self.getColor()}">{self.toStringShort()}{self.getDescriptionString()}</div>'


    def toSVG(self,x,y):

        """  """

        strResult = ''

        if self.duration is None or self.getDuration().total_seconds() < 60:
            strResult += '<text x="{}" y="{}">{}<title>{}</title></text>\n'.format(x + config.diagram_bar_height / 2, y + config.diagram_bar_height, self.getDescriptionSVG(), str(self))
        else:
            strResult += '<rect fill="{}"'.format(self.getColor())

            if self.dist is None or True:
                # "about 25 distance units per hour"
                bar_width = self.getDuration().total_seconds() / 3600 * 25 * config.diagram_scale_dist
            else:
                bar_width = self.dist * config.diagram_scale_dist

            if self.isMarked():
                strResult += ' stroke="red" stroke-width="1"'
            else:
                strResult += ' stroke="black" stroke-width=".5"'

            strResult += ' height="{}" width="{:.0f}" x="{}" y="{}"'.format(config.diagram_bar_height, bar_width, x, y)
            strResult += '>'

            strResult += '<title>{} {}</title>'.format(self.toStringShort(), self.getDescriptionString())

            strResult += '</rect>\n'

            if self.isMarked():
                strResult += '<text x="{}" y="{}">{}<title>{}</title></text>\n'.format(x + config.diagram_bar_height / 2 + bar_width, y + config.diagram_bar_height, self.getDescriptionString(), str(self))

        return strResult


    def toFreemindNode(self):

        """  """

        strResult = '<node'
        strResult += ' TEXT="' + self.toStringShort() + '"'
        strResult += ' BACKGROUND_COLOR="{}"'.format(self.getColor())
        strResult += '>'

        if self.dist is not None:
            strResult += '<node TEXT="' + self.getSpeedStr() + '"/>'

        strResult += self.getDescriptionFreemind()

        strResult += '</node>\n'

        return strResult


    def to_ical(self,cal):

        """  """

        event = Event()

        if self.type is None:
            if self.hasDescription():
                event.add('summary', self.getDescriptionString())
        else:
            event.add('summary', "{} {}".format(self.type, self.getDurationString()))
            if self.hasDescription():
                event.add('description', self.getDescriptionString())

        if event.is_empty():
            return
        elif self.dt is None:
            print('error ICAL: no date ' + str(self), file=sys.stderr)
            return
        elif self.dt.time() == time(0) or self.duration is None:
            # no time defined
            event.add('dtstart', self.dt.date())
            event.add('dtend', self.dt.date() + timedelta(days=1))
        else:
            event.add('dtstart', self.dt)
            event.add('dtend', self.dt + self.duration)

            # TODO: add reminder
            #alarm = Alarm()
            #alarm.add('action', 'DISPLAY')
            #alarm.add('trigger', self.dt - timedelta(minutes=15))
            #event.add_component(alarm)
        
        event.add('dtstamp', datetime.now().astimezone(None))
        cal.add_component(event)

