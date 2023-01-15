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

import re

import copy

from datetime import timedelta, date, datetime, time, timezone

from icalendar import Calendar, Event, Alarm

from training import config as config
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

        self.parse(strArg)


    def __str__(self):

        """  """

        if self.type == None and self.dist == None and self.dt == None:
            strResult = '-'
        elif self.type == None:
            strResult = '{} {}'.format(self.dt.isoformat(), str(self.getDuration()))
        elif self.dist == None and self.dt == None:
            strResult = '{} {---}'
        elif self.dist == None:
            strResult = '{} {} {}'.format(self.dt.isoformat(), self.type, str(self.getDuration()))
        elif self.dt == None:
            if self.clock == None:
                strResult = '{} {:5.1f} {} {}'.format('', self.dist, self.type, str(self.getDuration()))
            else:
                strResult = '{} {:5.1f} {} {}'.format(self.clock.isoformat(), self.dist, self.type, str(self.getDuration()))
        else:
            strResult = '{} {:5.1f} {} {}'.format(self.dt.isoformat(), self.dist, self.type, str(self.getDuration()))

        return strResult


    def setTypeStr(self,strArg):

        """  """

        if strArg == None or strArg == '':
            pass
        else:
            self.type = strArg.replace(' ','')[0:config.max_length_type]

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


    def setDurationStr(self,strArg):

        """  """

        if strArg == None or strArg == '':
            self.duration = None
        else:
            entry = strArg.split(':')
            if len(entry) == 1:
                # nothing to split
                entry = strArg.split('min')
                if len(entry) == 2:
                    self.duration = timedelta(minutes=float(entry[0]))
                else:
                    entry = strArg.split('h')
                    if len(entry) == 2:
                        self.duration = timedelta(hours=float(entry[0]))
                    else:
                        self.duration = None
            elif len(entry) == 2:
                self.duration = timedelta(minutes=int(entry[0]), seconds=int(entry[1]))
            elif len(entry) == 3:
                self.duration = timedelta(hours=int(entry[0]), minutes=int(entry[1]), seconds=int(entry[2]))
            else:
                self.duration = None

        return True


    def getDuration(self):

        """  """
        
        if self.duration == None:
            return timedelta(seconds=0)
        else:
            return self.duration


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
                s = self.getDuration().total_seconds()
                if s < 900.0:
                    self.duration *= floatScale
                else:
                    # round duration to 5:00 min
                    self.duration = timedelta(seconds=(round(s * floatScale / 300.0) * 300.0))

        return self


    def parse(self,objArg):

        """  """

        #self.__init__()
        
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
            if self.setDistStr(objArg[1]) and self.setTypeStr(objArg[2]) and self.setDurationStr(objArg[3]):
                self.setDateStr(objArg[0])
                self.appendDescription(objArg[4:])
                return True
            else:
                return False
        else:
            return False


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
                strResult = '{date};;;'.format(date=self.dt.isoformat())
            elif self.dist == None:
                strResult = '{date};;{type};{duration}'.format(date=self.dt.isoformat(), type=self.type, duration=str(self.getDuration()))
            else:
                strResult = '{date};{dist:.1f};{type};{duration}'.format(date=self.dt.isoformat(), dist=self.dist, type=self.type, duration=str(self.getDuration()))

            strResult += ';' + self.__listDescriptionToString__()

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

        strResult += str(self)
        strResult += '</p>'
        
        return strResult


    def toSVG(self,x,y):

        """  """

        strResult = ''

        if self.duration == None or self.getDuration().total_seconds() < 60:
            strResult += '<text x="{}" y="{}">{}<title>{}</title></text>\n'.format(x + config.diagram_bar_height / 2, y + config.diagram_bar_height, self.__listDescriptionToString__(), self.toString())
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

            strResult += '<title>{}: {}</title>'.format(self.toString(), self.__listDescriptionToString__())

            strResult += '</rect>\n'

        return strResult


    def toXML(self):

        """  """

        strResult = '<node'

        strResult += ' TEXT="' + self.toString() + '"'

        if self.type != None and len(self.type) > 0 and self.type[0] in config.colors:
            strResult += ' BACKGROUND_COLOR="{}"'.format(config.colors[self.type[0]])
        strResult += '>'

        if self.dist != None:
            strResult += '<node TEXT="' + self.getSpeedStr() + '"/>'

        strResult += self.__listDescriptionToXML__()

        strResult += '</node>\n'

        return strResult


    def to_ical(self,cal):

        """  """

        event = Event()

        if self.type == None:
            event.add('summary', self.__listDescriptionToString__())
        else:
            event.add('summary', "{} {}".format(self.type, str(self.getDuration())))
            if self.hasDescription():
                event.add('description', self.__listDescriptionToString__())

        if self.dt == None:
            pass
        elif self.dt.time().hour == 0 or self.duration == None:
            event.add('dtstart', self.dt.date())
            event.add('dtend', self.dt.date() + timedelta(days=1))
        else:
            event.add('dtstart', self.dt)
            event.add('dtend', self.dt + self.duration)

            # TODO: add reminder
            alarm = Alarm()
            alarm.add('action', 'none')
            alarm.add('trigger', self.dt - timedelta(minutes=15))
            event.add_component(alarm)
        
        event.add('dtstamp', datetime.now().astimezone(None))
        cal.add_component(event)

