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
from training.description import Description
from training.title import Title
#from training.unit import Unit
#from training.cycle import Cycle
#from training.period import Period

#
#
#

class Unit(Description):

    """ class for training units """

    def __init__(self,strArg=None):

        """ constructor """

        if strArg == None:
            self.reset()
        else:
            self.parse(strArg)


    def reset(self):

        """  """

        self.dist = None
        self.type = None
        self.duration = None
        self.date = None
        self.clock = None
        self.combined = False
        self.setDescription()

        return self


    def appendDescription(self,objArg):

        """  """

        if objArg != None and len(objArg) > 0:
            super().appendDescription(objArg)

        return self


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
            self.dist = float(strArg.replace(',','.'))
            if self.dist < 0.001:
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


    def getDurationStr(self):

        """  """

        strResult = ''
        
        if self.duration != None:
            seconds = self.duration.total_seconds()
            strResult = time(hour = int(seconds // 3600), minute = int((seconds % 3600) // 60), second = int(seconds % 60)).strftime("%H:%M:%S")

        return strResult


    def setDate(self,objArg):

        """  """

        if type(objArg) == date:
            self.date = objArg
        elif type(objArg) == time:
            self.clock = objArg
        else:
            print('ignoring: ',type(objArg), file=sys.stderr)
            
        return self


    def setDateStr(self,strArg):

        """  """

        if strArg == None or strArg == '':
            pass
        elif strArg == '+':
            # it's a combined unit (starts after its predecessor unit, same date)
            self.combined = True
        else:
            # canonical ISO Date+Time
            m = re.match(r"\s*([0-9]{4}-*[0-9]{2}-*[0-9]{2})[\sT]+([0-2][0-9]:[0-5]{2})\s*",strArg)
            if m != None:
                #print("date + time: ",m.group(1), " ",m.group(2))
                self.setDateStr(m.group(1))
                self.setDateStr(m.group(2))
            else:
                # german Date
                m = re.match(r"([0-9]{2})\.([0-9]{2})\.([0-9]{4})",strArg)
                if m != None:
                    try:
                        self.setDate(date(int(m.group(3)), int(m.group(2)), int(m.group(1))))
                    except ValueError as e:
                        print('error: ' + str(e), file=sys.stderr)
                        return False
                else:
                    # canonical ISO Date
                    m = re.match(r"([0-9]{4})-*([0-9]{2})-*([0-9]{2})",strArg)
                    if m != None:
                        try:
                            self.setDate(date(int(m.group(1)), int(m.group(2)), int(m.group(3))))
                        except ValueError as e:
                            print('error: ' + str(e), file=sys.stderr)
                            return False
                    else:
                        # clock only
                        m = re.match(r"([0-2][0-9]:[0-5]{2})",strArg)
                        if m != None:
                            #print("time: ",m.group(1), file=sys.stderr)
                            self.setDate(time.fromisoformat("{}:00".format(m.group(1))))
                        else:
                            print('ignoring: ',strArg, file=sys.stderr)

        return True


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
                s = self.duration.total_seconds()
                if s < 900.0:
                    self.duration *= floatScale
                else:
                    # round duration to 5:00 min
                    self.duration = timedelta(seconds=(round(s * floatScale / 300.0) * 300.0))

        return self


    def dup(self):

        """  """

        return copy.deepcopy(self)


    def parse(self,objArg):

        """  """

        if objArg == None or len(objArg) < 1:
            return False
        elif type(objArg) is str:
            entry = objArg.split(';')
            # TODO: test elements of entry
            if len(entry) == 3:
                entry.insert(0,'')
            return self.parse(entry)
        elif type(objArg) is list and len(objArg) > 3:
            self.reset()
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
            s = float(self.duration.total_seconds())
            if s < 1:
                pass
            else:
                spk = s / self.dist
                strResult += '{}:{:02} min/{} '.format(int(spk // 60), int(spk % 60), config.unit_distance)
                strResult += '{:.0f} {}/h '.format(self.dist / (s / 3600), config.unit_distance)

        return strResult


    def toString(self):

        """  """

        if self.type == None and self.dist == None and self.date == None:
            strResult = 'EMPTY'
        elif self.type == None:
            strResult = '{date} {duration}'.format(date=self.date.isoformat(), duration=self.getDurationStr())
        elif self.dist == None:
            strResult = '{date} {type} {duration}'.format(date=self.date.isoformat(), type=self.type, duration=self.getDurationStr())
        elif self.date == None:
            strResult = '{date} {dist:5.1f} {type} {duration}'.format(date='', dist=self.dist, type=self.type, duration=self.getDurationStr())
        else:
            strResult = '{date} {dist:5.1f} {type} {duration}'.format(date=self.date.isoformat(), dist=self.dist, type=self.type, duration=self.getDurationStr())

        return strResult


    def toCSV(self):

        """  """

        if self.type == None:
            strResult = '{date};;;'.format(date=self.date.isoformat())
        elif self.dist == None:
            strResult = '{date};;{type};{duration}'.format(date=self.date.isoformat(), type=self.type, duration=self.getDurationStr())
        else:
            strResult = '{date};{dist:.1f};{type};{duration}'.format(date=self.date.isoformat(), dist=self.dist, type=self.type, duration=self.getDurationStr())

        strResult += ';' + self.__listDescriptionToString__()

        return strResult


    def toSVG(self,x,y):

        """  """

        strResult = ''

        if self.duration == None or self.duration.total_seconds() < 60:
            strResult += '<text x="{}" y="{}">{}<title>{}</title></text>\n'.format(x + config.diagram_bar_height / 2, y + config.diagram_bar_height, self.__listDescriptionToString__(), self.toString())
        else:
            strResult += '<rect '

            if self.type == None or len(self.type) < 1:
                strResult += ' fill="{}"'.format('#cccccc')
            elif self.type[0] in config.colors:
                strResult += ' fill="{}"'.format(config.colors[self.type[0]])

            if self.dist == None or True:
                # "about 25 distance units per hour"
                bar_width = self.duration.total_seconds() / 3600 * 25 * config.diagram_scale_dist
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


    def toiCalString(self):

        """  """

        dateNow = datetime.now()

        strResult = 'BEGIN:VEVENT\n'

        if self.type == None:
            strResult += "SUMMARY:{description}\n".format(description = self.__listDescriptionToString__())
        else:
            strResult += "SUMMARY:{type} {time}\n".format(type=self.type, time=self.getDurationStr())
            if self.hasDescription():
                strResult += 'DESCRIPTION:{}\n'.format(self.__listDescriptionToString__())

        if self.clock == None or self.duration == None:
            strResult += self.date.strftime("DTSTART;%Y%m%d\nDTEND;%Y%m%d\n")
        else:
            t0 = datetime.combine(self.date, self.clock).astimezone(tz=LOCAL)
            t1 = t0 + self.duration

            if sun != None:
                # fix 't' according to sunrise/sunset
                t_earliest = sun.get_local_sunrise_time(self.date) + timedelta(seconds=twilight)
                t_latest = sun.get_local_sunset_time(self.date) - timedelta(seconds=twilight)

                if t_earliest > t0:
                    # shift start time after twilight
                    t0 = t_earliest
                    # adjust to 15min steps
                    t0 -= timedelta(minutes=(t0.minute % 15))
                    t1 = t0 + self.duration
                elif t_latest < t1:
                    # shift end time before twilight
                    t0 = t_latest - self.duration
                    t0 -= timedelta(minutes=(t0.minute % 15))
                    t1 = t0 + self.duration

            #print(self.date,' ',self.clock,' ',self.type,' ',t0,' ',t_latest,file=sys.stderr)

            strResult += t0.strftime("DTSTART;%Y%m%dT%H%M%S\n")
            strResult += t1.strftime("DTEND;%Y%m%dT%H%M%S\n")

        strResult += dateNow.strftime("DTSTAMP;%Y%m%dT%H%M%S\n")

        strResult += 'END:VEVENT\n'

        return strResult


    def to_ical(self,cal):

        """  """

        event = Event()

        if self.type == None:
            event.add('summary', self.__listDescriptionToString__())
        else:
            event.add('summary', "{} {}".format(self.type, self.getDurationStr()))
            if self.hasDescription():
                event.add('description', self.__listDescriptionToString__())

        # TODO: handle start time of combined units to_ical(self,cal,predecessor_end)

        if self.clock == None or self.duration == None:
            event.add('dtstart', self.date)
            event.add('dtend', self.date + timedelta(days=1))
        else:
            t0 = datetime.combine(self.date, self.clock).astimezone(None)
            t1 = t0 + self.duration

            if config.sun != None:
                # fix 't' according to sunrise/sunset
                t_earliest = config.sun.get_local_sunrise_time(self.date) + timedelta(seconds=config.twilight)
                t_latest = config.sun.get_local_sunset_time(self.date) - timedelta(seconds=config.twilight)

                if t_earliest > t0:
                    # shift start time after twilight
                    t0 = t_earliest
                    # adjust to 15min steps
                    t0 -= timedelta(minutes=(t0.minute % 15))
                    t1 = t0 + self.duration
                elif t_latest < t1:
                    # shift end time before twilight
                    t0 = t_latest - self.duration
                    t0 -= timedelta(minutes=(t0.minute % 15))
                    t1 = t0 + self.duration

            #print(self.date,' ',self.clock,' ',self.type,' ',t0,' ',t_latest,file=sys.stderr)

            event.add('dtstart', t0)
            event.add('dtend', t1)

            # TODO: add reminder
            alarm = Alarm()
            alarm.add('action', 'none')
            alarm.add('trigger', t0 - timedelta(minutes=15))
            event.add_component(alarm)
        
        event.add('dtstamp', datetime.now().astimezone(None))
        cal.add_component(event)



if __name__ == "__main__":
    
    print('Module Test:\n')
    
    #u = Unit('2020-13-33T27:00:00+1:00;10;RG;20min')

    u = Unit('2020-03-03T17:00:00+1:00;10;RG;20min')

    print(u.toString())

