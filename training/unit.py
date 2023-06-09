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

        self.setDuration()

        self.parse(strArg)


    def __str__(self):

        """  """

        if self.type == None and self.dist == None and self.dt == None:
            strResult = '-'
        elif self.type == None:
            if self.dt == None or self.dt.time() == time(0):
                strResult = '{} {}'.format(self.dt.strftime("%Y-%m-%d"), str(self.getDuration()))
            else:
                strResult = '{} {}'.format(self.dt.strftime("%Y-%m-%d %H:%M:%S"), str(self.getDuration()))
        elif self.dist == None:
            if self.dt == None:
                strResult = '{} {}'.format(self.type, str(self.getDuration()))
            elif self.dt.time() == time(0):
                strResult = '{} {} {}'.format(self.dt.strftime("%Y-%m-%d"), self.type, str(self.getDuration()))
            else:
                strResult = '{} {} {}'.format(self.dt.strftime("%Y-%m-%d %H:%M:%S"), self.type, str(self.getDuration()))
        elif self.dt == None:
            strResult = '{:5.1f} {} {}'.format(self.dist, self.type, str(self.getDuration()))
        elif self.dt.time() == time(0):
            strResult = '{} {:5.1f} {} {}'.format(self.dt.strftime("%Y-%m-%d"), self.dist, self.type, str(self.getDuration()))
        else:
            strResult = '{} {:5.1f} {} {}'.format(self.dt.strftime("%Y-%m-%d %H:%M:%S"), self.dist, self.type, str(self.getDuration()))

        return strResult


    def setDate(self,dtArg=None,dt_0=None,dt_1=None):

        """ fix 'dt' according to sunrise dt_0 or sunset dt_1 """

        #print('setDate(' + dtArg.isoformat() + ' '  + dt_0.isoformat() + ' ' + dt_1.isoformat() + ') = ' + self.dt.isoformat() , file=sys.stderr)

        if dtArg == None:
            
            self.dt = None
            return self.dt
        
        elif type(dtArg) == date:
            
            return self.setDate(datetime.combine(dtArg,time(0)).astimezone(None),dt_0,dt_1)

        elif type(dtArg) == datetime:

            if self.tPlan == None:
                self.dt = dtArg
            elif type(self.tPlan) == str and self.tPlan == 'sunrise' and dt_0 != None:
                # shift start time after twilight
                self.dt = dt_0
                # adjust to 15min steps
                self.dt -= timedelta(minutes=(self.dt.minute % 15))
            elif type(self.tPlan) == str and self.tPlan == 'sunset' and dt_1 != None:
                # shift end time before twilight
                self.dt = dt_1 - self.duration
                self.dt -= timedelta(minutes=(self.dt.minute % 15))
            elif type(self.tPlan) == time:
                self.dt = datetime.combine(dtArg.date(),self.tPlan).astimezone(None)
            else:
                #self.dt = datetime.combine(dtArg.date(),time(0)).astimezone(None)
                self.dt = dtArg
        
        else:
            print('error: date type unknown', file=sys.stderr)
                
        return self.dt + self.duration
        

    def setTypeStr(self,strArg):

        """  """

        if strArg == None or strArg == '':
            pass
        elif config.max_length_type > 0 and config.max_length_type < 32:
            self.type = strArg[0:config.max_length_type]
        else:
            self.type = strArg

        return True


    def setDistStr(self,strArg):

        """  """

        if strArg == None or strArg == '':
            self.dist = None
        else:
            try:
                self.dist = float(strArg.replace(',','.'))
                if self.dist < 0.001:
                    self.dist = None
            except ValueError:
                self.dist = None

        return True


    def setDuration(self,intArg=None):

        """  """

        if intArg == None:
            self.duration = Duration(0)
        else:
            self.duration = Duration(intArg)

        return True


    def getDuration(self):

        """  """
        
        if self.duration == None:
            self.setDuration()

        if self.type != None and len(self.type) > 0:
            return self.duration

        return Duration(0)


    def scale(self,floatScale,patternType=None):

        """  """

        if floatScale > 0.1 and (patternType == None or self.type == None or re.match(patternType,self.type)):

            if self.dist != None:
                if self.dist < 15.0:
                    self.dist *= floatScale
                else:
                    # round distance to 5.0
                    self.dist = round(self.dist * floatScale / 5.0) * 5.0

            if self.duration != None:
                self.duration.scale(floatScale)

        return self


    def parse(self,objArg):

        """  """
        
        if objArg == None or len(objArg) < 1:
            return False
        elif type(objArg) is str:
            entry = objArg.split(';')
            # TODO: test elements of entry
            if len(entry) == 1:
                # type only
                entry.insert(0,'')
                entry.insert(0,'')
                entry.append('')
            elif len(entry) == 2:
                # type + time only
                entry.insert(0,'')
                entry.append('')
            elif len(entry) == 3:
                # dist + type + time
                entry.insert(0,'')
            return self.parse(entry)
        elif type(objArg) is list and len(objArg) > 3:
            if self.setDistStr(objArg[1]) and self.setTypeStr(objArg[2]) and self.setDuration(objArg[3]):
                self.setDateStr(objArg[0])
                self.appendDescription(objArg[4:])
                return True
            else:
                return False
        else:
            return False


    def stat(self, dictArg):

        """  """

        if dictArg == None:
            print('error: ' + 'no dict', file=sys.stderr)
        elif self.type != None and len(self.type) > 0:
            if self.type not in dictArg:
                dictArg[self.type] = [[],[]]
                
            if self.dist != None:
                dictArg[self.type][0].append(self.dist)
            else:
                dictArg[self.type][0].append(0.0)
                
            dictArg[self.type][1].append(self.getDuration().total_seconds())


    def getSpeedStr(self):

        """  """

        strResult = ''
        if self.dist == None or self.duration == None:
            pass
        else:
            s = float(self.getDuration().total_seconds())
            if s < 1:
                pass
            else:
                spk = s / self.dist
                strResult += '{}:{:02} min/{} '.format(int(spk // 60), int(spk % 60), config.unit_distance)
                strResult += '{:.0f} {}/h '.format(self.dist / (s / 3600), config.unit_distance)

        return strResult


    def toCSV(self):

        """  """

        if self.dt == None:
            strResult = ''
        else:
            if self.type == None:
                strResult = '{date};;;'.format(date=self.dt.strftime("%Y-%m-%d"))
            elif self.dist == None:
                strResult = '{date};;{type};{duration}'.format(date=self.dt.strftime("%Y-%m-%d"), type=self.type, duration=str(self.getDuration()))
            else:
                strResult = '{date};{dist:.1f};{type};{duration}'.format(date=self.dt.strftime("%Y-%m-%d"), dist=self.dist, type=self.type, duration=str(self.getDuration()))

            strResult += ';' + self.__listDescriptionToString__()

        return strResult


    def toSqlite(self):

        """  """

        if self.dt == None or self.type == None or self.dist == None:
            # not significant for reports
            strResult = ''
        else:
            strResult = "INSERT INTO 'units' VALUES ('{date}',{dist:.1f},'{type}','{duration}','{description}');\n".format(date=self.dt.strftime("%Y-%m-%d"), dist=self.dist, type=self.type, duration=str(self.getDuration()), description=self.__listDescriptionToString__())

        return strResult


    def toHtml(self):

        """  """

        strResult = '<p'
        if self.type == None or len(self.type) < 1:
            strResult += ' style="background-color: {}"'.format('#cccccc')
        elif self.type[0] in config.colors:
            strResult += ' style="background-color: {}"'.format(config.colors[self.type[0]])
        elif self.color != None:
            strResult += ' style="background-color: {}"'.format(self.color)
        strResult += '>'

        strResult += str(self) + ' ' + self.__listDescriptionToString__()
        strResult += '</p>'
        
        return strResult


    def toSVG(self,x,y):

        """  """

        strResult = ''

        if self.duration == None or self.getDuration().total_seconds() < 60:
            strResult += '<text x="{}" y="{}">{}<title>{}</title></text>\n'.format(x + config.diagram_bar_height / 2, y + config.diagram_bar_height, self.__listDescriptionToSVG__(), str(self))
        else:
            strResult += '<rect '

            if self.type == None or len(self.type) < 1:
                strResult += ' fill="{}"'.format('#cccccc')
            elif self.type[0] in config.colors:
                strResult += ' fill="{}"'.format(config.colors[self.type[0]])

            if self.dist == None or True:
                # "about 25 distance units per hour"
                bar_width = self.getDuration().total_seconds() / 3600 * 25 * config.diagram_scale_dist
            else:
                bar_width = self.dist * config.diagram_scale_dist

            strResult += ' height="{}" stroke="black" stroke-width=".5" width="{:.0f}" x="{}" y="{}"'.format(config.diagram_bar_height, bar_width, x, y)
            strResult += '>'

            strResult += '<title>{}: {}</title>'.format(str(self), self.__listDescriptionToString__())

            strResult += '</rect>\n'

        return strResult


    def toFreemindNode(self):

        """  """

        strResult = '<node'

        strResult += ' TEXT="' + str(self) + '"'

        if self.type != None and len(self.type) > 0 and self.type[0] in config.colors:
            strResult += ' BACKGROUND_COLOR="{}"'.format(config.colors[self.type[0]])
        strResult += '>'

        if self.dist != None:
            strResult += '<node TEXT="' + self.getSpeedStr() + '"/>'

        strResult += self.__listDescriptionToFreemind__()

        strResult += '</node>\n'

        return strResult


    def to_ical(self,cal):

        """  """

        event = Event()

        if self.type == None:
            if self.hasDescription():
                event.add('summary', self.__listDescriptionToString__())
        else:
            event.add('summary', "{} {}".format(self.type, str(self.getDuration())))
            if self.hasDescription():
                event.add('description', self.__listDescriptionToString__())

        if event.is_empty():
            return
        elif self.dt == None:
            print('error: ' + str(self), file=sys.stderr)
            return
        elif self.dt.time() == time(0) or self.duration == None:
            # no time defined
            event.add('dtstart', self.dt.date())
            event.add('dtend', self.dt.date() + timedelta(days=1))
        else:
            event.add('dtstart', self.dt)
            event.add('dtend', self.dt + self.duration)

            # TODO: add reminder
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('trigger', self.dt - timedelta(minutes=15))
            event.add_component(alarm)
        
        event.add('dtstamp', datetime.now().astimezone(None))
        cal.add_component(event)

