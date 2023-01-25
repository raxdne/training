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

        """  """

        super().__init__()
        
        self.dt = None
        self.tPlan = None

        if strArg != None and len(strArg) > 0:
            self.parse(strArg)
            #print('New Unit: ' + strArg + ' -> {} {} {} {} {}'.format(self.dt, self.dist, self.type, self.duration, self.__listDescriptionToString__()), file=sys.stderr)


    def __str__(self):

        """  """

        strResult = ''
        if self.dt != None:
            strResult += self.dt.strftime("%Y-%m-%d")
            
        strResult += super().__str__()

        return strResult


    def appendDescription(self,objArg):

        """  """

        super().appendDescription(objArg)

        return self


    def setClock(self,timeArg=None):

        """  """

        self.tPlan = timeArg

        return True


    def setDate(self,dtArg=None,dt_0=None,dt_1=None):

        """  """

        if dtArg == None:
            self.dt = None
        elif type(dtArg) == date:
            if self.tPlan == None:
                return self.setDate(datetime.combine(dtArg,time(0)).astimezone(None),dt_0,dt_1)
            else:
                return self.setDate(datetime.combine(dtArg,self.tPlan).astimezone(None),dt_0,dt_1)
        elif type(dtArg) == datetime:
            if self.tPlan != None and dtArg.time() == time(0):
                return self.setDate(datetime.combine(dtArg.date(),self.tPlan).astimezone(None),dt_0,dt_1)
            else:
                self.dt = dtArg
                return self.dt
        else:
            print('error: ' + str(dtArg), file=sys.stderr)

        return None


    def setDateStr(self,strArg):

        """  """

        if strArg == None or strArg == '':
            pass
        elif strArg == '+':
            # it's a combined unit (starts after its predecessor unit, same date)
            pass
        elif strArg == 'sr':
            self.tPlan = 'sunrise'
        elif strArg == 'ss':
            self.tPlan = 'sunset'
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
                        # plan time only
                        m = re.match(r"([0-2][0-9]:[0-5][0-9])",strArg)
                        if m != None:
                            #print("time: ",m.group(1), file=sys.stderr)
                            self.tPlan = time.fromisoformat("{}:00".format(m.group(1)))
                        else:
                            print('ignoring: ',strArg, file=sys.stderr)

        return True


    def dup(self):

        """  """

        return copy.deepcopy(self)


    def parse(self,objArg):

        """  """

        #self.__init__()
        
        if objArg == None or len(objArg) < 1:
            return False
        elif type(objArg) is str:
            entry = objArg.split(';')
            #print('Note {}'.format(str(entry)), file=sys.stderr)
            if len(entry) == 1:
                self.appendDescription(objArg)
                return True
            elif len(entry) == 2:
                self.setDateStr(entry[0])
                self.appendDescription(entry[1:])
                return True
            else:
                return self.parse(entry)
        elif type(objArg) is list and len(objArg) > 3:
            if len(objArg[0]) > 0 and len(objArg[1]) == 0 and len(objArg[2]) == 0 and  len(objArg[3]) == 0 and (len(objArg[4]) > 0 or len(objArg[5]) > 0):
                self.setDateStr(objArg[0])
                self.appendDescription(objArg[4:])
                #print('Note {}'.format(str(self)), file=sys.stderr)
                return True
            else:
                return False
        else:
            return False


    def toString(self):

        """  """

        return str(self)


    def toHtml(self):

        """  """

        strResult = '<p>' + str(self) + '</p>'
        
        return strResult


    def toCSV(self):

        """  """

        strResult = ';' + self.__listDescriptionToString__()

        return strResult


    def toSVG(self,x,y):

        """  """

        strResult = '<text x="{}" y="{}">{}<title>{}</title></text>\n'.format(x + config.diagram_bar_height / 2, y + config.diagram_bar_height, self.__listDescriptionToString__(), str(self))

        return strResult


    def toFreemind(self):

        """  """

        strResult = '<node'

        if self.dt != None:
            strResult += ' TEXT="' + self.dt.strftime("%Y-%m-%d") + '"'
            
        strResult += '>'

        strResult += self.__listDescriptionToFreemind__()

        strResult += '</node>\n'

        return strResult


    def to_ical(self,cal):

        """  """

        if self.dt != None:
            event = Event()

            event.add('summary', self.__listDescriptionToString__())
            event.add('dtstart', self.dt.date())
            event.add('dtend', self.dt.date() + timedelta(days=1))
        
            event.add('dtstamp', datetime.now().astimezone(None))
            cal.add_component(event)


