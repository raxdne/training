#
# Data Management for Physical Training
#
# Copyright (C) 2021,2022,2023,2026 by Alexander Tenbusch
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
from training.titem import TItem

#
#
#

class Unit(TItem):

    """ class for training units """

    def __init__(self,s=None):

        """  """

        super().__init__()
        
        self._dist = None
        self._type = None
        self.d = 0

        if s is not None and len(s) > 0:
            self.parse(s)


    def __repr__(self):

        strResult = f'{self.__class__.__name__}([{self.dt!r},{self._dist!r},{self.type!r},{self._d!r}])'
        if self.hasDescription():
            strResult += f'.appendDescription({self.description!r})'

        return strResult


    def __str__(self):

        """  """

        if self.type is None and self._dist is None and self.dt is None:
            strResult = '-'
        elif self.type is None:
            if self.dt is None or self.dt.time() == time(0):
                strResult = f'{self.dt.strftime("%Y-%m-%d")} {str(self._d)}'
            else:
                strResult = f'{self.dt.strftime("%Y-%m-%d %H:%M:%S")} {str(self._d)}'
        elif self._dist is None:
            if self.dt is None:
                strResult = f'{self.type} {str(self._d)}'
            elif self.dt.time() == time(0):
                strResult = f'{self.dt.strftime("%Y-%m-%d")} {self.type} {str(self._d)}'
            else:
                strResult = f'{self.dt.strftime("%Y-%m-%d %H:%M:%S")} {self.type} {str(self._d)}'
        elif self.dt is None:
            strResult = f'{self.getDistString():>7} {self.type} {str(self._d)}'
        elif self.dt.time() == time(0):
            strResult = f'{self.dt.strftime("%Y-%m-%d")} {self.getDistString():>7} {self.type} {str(self._d)}'
        else:
            strResult = f'{self.dt.strftime("%Y-%m-%d %H:%M:%S")} {self.getDistString():>7} {self.type} {str(self._d)}'

        if self.isMarked():
            strResult += '*'
    
        return strResult


    def toStringShort(self):

        """  """
    
        strResult = ''

        if self._dist is not None:
            strResult += self.getDistString() + ' '
        
        if self.type is not None:
            strResult += self.type + ' '

        strResult += str(self._d)

        return strResult


    def set(self,**kwargs):
        
        """ generic setter """
        
        for key, value in kwargs.items():
            if key in ['dt','color','type','dist','description','marker','d']:
                setattr(self, key, value)

        return self


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
                self.dt = dt_1 - self._d
                self.dt -= timedelta(minutes=(self.dt.minute % 15))
            elif type(self.tPlan) is time:
                self.dt = datetime.combine(dtArg.date(),self.tPlan).astimezone(None)
            else:
                #self.dt = datetime.combine(dtArg.date(),time(0)).astimezone(None)
                self.dt = dtArg
        
        else:
            print('error: date type unknown', file=sys.stderr)
                
        return self.dt + self._d
        

    schedule = setDate


    @property
    def type(self):

        """  """

        return self._type


    @type.setter
    def type(self, s):

        """  """

        if s is None or len(s) < 1:
            pass
        elif config.max_length_type > 0 and config.max_length_type < 32:
            self._type = s[0:config.max_length_type]
        else:
            self._type = s


    def setTypeStr(self,strArg):

        """ legacy """

        self.type = strArg

        return True


    @property
    def dist(self):

        """  """

        return self._dist


    @dist.setter
    def dist(self, o):

        """  """

        if o is None:
            self._dist = None
        elif isinstance(o,int):
            self._dist = float(o)
        elif isinstance(o,float):
            self._dist = o
        elif isinstance(o,str):
            try:
                self._dist = float(o.replace(',','.'))
            except ValueError:
                self._dist = None
        else:
            return NotImplemented

        if self._dist is not None and self._dist < 0.001:
            self._dist = None


    def setDistStr(self,strArg=None):

        """ legacy """

        self.dist = strArg

        return (self.dist is not None and self.dist > 0.1)


    def getDistString(self):

        """  """

        strResult = ''
        
        if self._dist is None:
            pass
        elif self._dist < 1.0:
             strResult = '{:.02f} {}'.format(self._dist, config.unit_distance)
        elif self._dist < 10.0:
             strResult = '{:.1f} {}'.format(self._dist, config.unit_distance)
        else:
             strResult = '{:.0f} {}'.format(self._dist, config.unit_distance)

        return strResult


    @property
    def d(self):

        """  """

        return self._d


    @d.setter
    def d(self, *args, **kwargs):

        """  """

        self._d = Duration(*args, **kwargs)


    def getDuration(self, skipType=None):

        """  """
        
        if self.type is None or (skipType is not None and re.match(skipType,self.type)):
            # ignoring no types and skip pattern matches
            pass
        elif self.type is not None and self.type:
            return self.d

        return Duration(0)


    def updateValues(self,dictArg=None):

        """ update missing values for distance, duration and color """

        if dictArg is not None:
            if self.type is not None and self.type in dictArg and dictArg[self.type] > 1.0 and self._d is not None and self._d > Duration(0):
                if self._dist is None or self._dist < 0.1:
                    # there is a defined default velocity
                    self._dist = dictArg[self.type] * (self._d.total_seconds() / 3600)
                    #print('info updating distance: ' + str(self), file=sys.stderr)
            elif self.type is not None and self.type in dictArg and dictArg[self.type] > 1.0 and self._dist is not None and self._dist > 0.1:
                if self._d is None or self._d < Duration(1):
                    # there is a defined default velocity
                    self.d = int(self._dist / dictArg[self.type] * 60)
                    #print('info updating duration: ' + str(self), file=sys.stderr)

        if hasattr(self,'color') and self.color is not None:
            pass
        elif self.type is None or not self.type:
            self.set(color='#cccccc')
        elif self.type in config.colors:
            self.set(color=config.colors[self.type])
        elif self.type[0] in config.colors:
            self.set(color=config.colors[self.type[0]])


    def match(self,p=None):
                            
       return (self.type is None or p is None or re.match(p,self.type))


    def isCountable(self):

        """  """

        return ((type(self.type) is str and self.type) and ((type(self._dist) is float and self._dist > 0.0) or self._d.total_seconds() > 0))


    def scale(self,f,p=None):

        """ returns a scaled copy of self """

        r = self.dup()
        if f > 0.01 and  abs(f - 1.0) > 0.01 and (p is None or r.type is None or re.match(p,r.type)):
            if r._dist is not None:
                if r._dist < 20.0:
                    r._dist *= f
                else:
                    # round distance to 5.0
                    r._dist = round(r._dist * f / 5.0) * 5.0

            r.d = r.d.scale(f)

        return r


    def parse(self,o):

        """  """
        
        if o is None or not o:
            return False
        elif type(o) is str:
            entry = o.split(';')
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
                # _dist + type + time
                entry.insert(0,'')
            return self.parse(entry)
        elif type(o) is list and len(o) > 3:

            if self.setTypeStr(o[2]):
                self.d = o[3]
                if self.setDistStr(o[1]):
                    pass
                else:
                    self.setDistStr()

                self.setDateStr(o[0])
                self.appendDescription(o[4:])
                return True
            else:
                return False
        else:
            return False


    def stat(self, skipType=None):

        """  """

        listResult = []
        
        if self.type is None or (skipType is not None and re.match(skipType,self.type)):
            # ignoring no types and skip pattern matches
            pass
        elif self._dist is None or self._dist < 0.001:
            #print('error: ' + 'no _dist', file=sys.stderr)
            listResult = [[0, 0.0, self._d.total_seconds() / 60, self.type]]
        elif self._d is None:
            #print('error: ' + 'no duration', file=sys.stderr)
            listResult = [[0, self._dist, 0.0, self.type]]
        elif self.dt is None:
            listResult = [[0, self._dist, self._d.total_seconds() / 60, self.type]]
        else:
            listResult = [[self.dt.toordinal(), self._dist, self._d.total_seconds() / 60, self.type]]

        return listResult


    def getSpeedStr(self):

        """  """

        strResult = ''
        if self._dist is None or self._d is None:
            pass
        else:
            s = float(self._d.total_seconds())
            if s < 1:
                pass
            else:
                min, sec = divmod(s / self._dist, 60)
                strResult += f'{min:0.0f}:{sec:02.0f} min/{config.unit_distance} '
                strResult += f'{self._dist / (s / 3600):.0f} {config.unit_distance}/h '

        return strResult


    def toCSV(self):

        """  """

        if self.dt is None:
            strResult = ''
        else:
            if self.type is None:
                strResult = '{date};;;'.format(date=self.dt.strftime("%Y-%m-%d"))
            elif self._dist is None:
                strResult = '{date};;{type};{duration}'.format(date=self.dt.strftime("%Y-%m-%d"), type=self.type, duration=self.d)
            else:
                strResult = '{date};{_dist:.1f};{type};{duration}'.format(date=self.dt.strftime("%Y-%m-%d"), dist=self._dist, type=self.type, duration=self.d)

            strResult += ';' + self.getDescriptionString() + '\n'

        return strResult


    def toSqlite(self):

        """  """

        if self.dt is None or self.type is None or self._dist is None:
            # not significant for reports
            strResult = ''
        else:
            strResult = "INSERT INTO 'units' VALUES ('{date}',{_dist:.1f},'{type}','{duration}','{description}');\n".format(date=self.dt.strftime("%Y-%m-%d"), dist=self._dist, type=self.type, duration=self.d, description=self.getDescriptionString())

        return strResult


    def toHtmlTable(self):

        """  """

        return f'<div {config.getClass(__name__)} style="background-color: {self.color}">{self.toStringShort()}{self.getDescriptionHTML()}</div>'


    def toSVG(self,x,y):

        """  """

        strResult = ''

        if self._d.total_seconds() < 60:
            strResult += '<text x="{}" y="{}">{}<title>{}</title></text>\n'.format(x + config.diagram_bar_height / 2, y + config.diagram_bar_height, self.getDescriptionSVG(), str(self))
        else:
            strResult += '<rect fill="{}"'.format(self.color)

            if self._dist is None or True:
                # "about 25 distance units per hour"
                bar_width = self._d.total_seconds() / 3600 * 25 * config.diagram_scale_dist
            else:
                bar_width = self._dist * config.diagram_scale_dist

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

        strResult = f'<node BACKGROUND_COLOR="{self.color}" TEXT="{self.toStringShort()}">'
        if self._dist is not None:
            strResult += f'<node TEXT="{self.getSpeedStr()}"/>'
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
            event.add('summary', "{} {}".format(self.type, str(self._d)))
            if self.hasDescription():
                event.add('description', self.getDescriptionString())

        if event.is_empty():
            return
        elif self.dt is None:
            print('error ICAL: no date ' + str(self), file=sys.stderr)
            return
        elif self.dt.time() == time(0) or self._d is None:
            # no time defined
            event.add('dtstart', self.dt.date())
            event.add('dtend', self.dt.date() + timedelta(days=1))
        else:
            event.add('dtstart', self.dt)
            event.add('dtend', self.dt + self._d)

            # TODO: add reminder
            #alarm = Alarm()
            #alarm.add('action', 'DISPLAY')
            #alarm.add('trigger', self.dt - timedelta(minutes=15))
            #event.add_component(alarm)
        
        event.add('dtstamp', datetime.now().astimezone(None))
        cal.add_component(event)


if __name__ == '__main__':

    print('Module Test: ' + __file__ + '\n')
    
    t = Unit(';;RB;0:30:00').appendDescription('First Test')
    t.setDate(date(2023,11,22))
    t.d = 123

    print(t)
