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

import copy

import re

from datetime import timedelta, date, datetime, time, timezone

from icalendar import Calendar, Event, Alarm

from training import config as config
from training.description import Description

#
#
#

class Note(Description):

    """ basis class for standalone notes and for training units """

    def __init__(self,strArg=None):

        """ constructor """

        super().__init__()
        
        self.dt = None
        self.clock = None
        
        if strArg == None:
            self.reset()
        else:
            self.parse(strArg)
            #print('New Unit: ' + strArg + ' -> {} {} {} {} {}'.format(self.dt, self.dist, self.type, self.duration, self.__listDescriptionToString__()), file=sys.stderr)


    def __str__(self):

        """  """

        strResult = ''
        if self.dt != None:
            strResult += self.dt.isoformat()
            
        strResult += super().__str__()

        return strResult


    def reset(self):

        """  """

        self.dt = None
        self.clock = None
        
        super().setDescription()

        return self


    def appendDescription(self,objArg):

        """  """

        super().appendDescription(objArg)

        return self


    def setClock(self,timeArg):

        """  """

        if timeArg == None:
            pass
        else:
            self.clock = timeArg

        return True


    def setDate(self,dateArg):

        """  """

        if dateArg == None:
            pass
        elif self.clock == None:
            self.dt = datetime.combine(dateArg,time(0)).astimezone(None)
        else:
            self.dt = datetime.combine(dateArg,self.clock).astimezone(None)

        return True


    def setDateStr(self,strArg):

        """  """

        if strArg == None or strArg == '':
            pass
        elif strArg == '+':
            # it's a combined unit (starts after its predecessor unit, same date)
            self.combined = True
        else:
            # canonical ISO Date+Time
            m = re.match(r"\s*([0-9]{4}-*[0-9]{2}-*[0-9]{2})[\sT]+([0-2][0-9]:[0-5][0-9])\s*",strArg)
            if m != None:
                try:
                    self.dt = datetime.fromisoformat(m.group(0)).astimezone(None)
                except ValueError as e:
                    print('error: ' + str(e), file=sys.stderr)
                    return False
            else:
                # german Date
                m = re.match(r"([0-9]{2})\.([0-9]{2})\.([0-9]{4})",strArg)
                if m != None:
                    try:
                        self.dt = datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)),0,0,0).astimezone(None)
                    except ValueError as e:
                        print('error: ' + str(e), file=sys.stderr)
                        return False
                else:
                    # canonical ISO Date
                    m = re.match(r"([0-9]{4})-*([0-9]{2})-*([0-9]{2})",strArg)
                    if m != None:
                        try:
                            self.dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),0,0,0).astimezone(None)
                        except ValueError as e:
                            print('error: ' + str(e), file=sys.stderr)
                            return False
                    else:
                        # clock only
                        m = re.match(r"([0-2][0-9]:[0-5][0-9])",strArg)
                        if m != None:
                            #print("time: ",m.group(1), file=sys.stderr)
                            self.clock = time.fromisoformat("{}:00".format(m.group(1)))
                        else:
                            print('ignoring: ',strArg, file=sys.stderr)

        return True


    def dup(self):

        """  """

        return copy.deepcopy(self)


    def parse(self,objArg):

        """  """

        self.reset()
        
        if objArg == None or len(objArg) < 1:
            return False
        elif type(objArg) is str:
            #entry = objArg.split(';')
            #return self.parse(entry)
            self.appendDescription(objArg)
            return True
        elif type(objArg) is list and len(objArg) > 0:
            self.appendDescription(objArg)
            return True
        else:
            return False


    def toString(self):

        """  """

        return str(self)


    def toHtml(self):

        """  """

        strResult = '<p>'
        if self.dt != None:
            strResult += self.dt.isoformat() + ' '
        strResult += self.__listDescriptionToString__()
        strResult += '</p>'
        
        return strResult


    def toCSV(self):

        """  """

        strResult = ';' + self.__listDescriptionToString__()

        return strResult


    def toSVG(self,x,y):

        """  """

        strResult = '<text x="{}" y="{}">{}<title>{}</title></text>\n'.format(x + config.diagram_bar_height / 2, y + config.diagram_bar_height, self.__listDescriptionToString__(), self.toString())

        return strResult


    def toXML(self):

        """  """

        strResult = self.__listDescriptionToXML__()

        return strResult


    def to_ical(self,cal):

        """  """

        event = Event()

        event.add('summary', self.__listDescriptionToString__())

        if self.dt == None:
            pass
        else:
            event.add('dtstart', self.dt)
            event.add('dtend', self.dt)

            # TODO: add reminder
            alarm = Alarm()
            alarm.add('action', 'none')
            alarm.add('trigger', self.dt - timedelta(minutes=15))
            event.add_component(alarm)
        
        event.add('dtstamp', datetime.now().astimezone(None))
        cal.add_component(event)


