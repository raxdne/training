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

import copy

import re

from datetime import timedelta, date, datetime, time, timezone

from icalendar import Calendar, Event, Alarm

from training import config as config
from training.titem import TItem

#
#
#

class Note(TItem):

    """ basis class for standalone notes and for training units """

    def __repr__(self):

        strResult = f'{self.__class__.__name__}({self.dt!r})'
        if self.hasDescription():
            strResult += f'.appendDescription({self.listDescription!r})'

        return strResult


    def __str__(self):

        """  """

        if self.dt is None:
            strResult = ''
        elif type(self.dt) is date or self.dt.time() == time(0):
            strResult = self.dt.strftime("%Y-%m-%d")
        else:
            strResult = self.dt.strftime("%Y-%m-%d %H:%M:%S")
            
        strResult += ' ' + self.getDescriptionString()

        return strResult


    def stat(self, skipType=None):

        """  """
        
        return self


    def toHtmlTable(self):

        """  """

        return f'<div {config.getClass(__name__)} style="background-color: {self.getColor()}">{self.getDescriptionString()}</div>'


    def toCSV(self):

        """  """

        strResult = '{};;;;{}\n'.format(self.dt.strftime("%Y-%m-%d"), self.getDescriptionString())

        return strResult


    def toSVG(self,x,y):

        """  """

        strResult = '<text x="{}" y="{}">{}<title>{}</title></text>\n'.format(x + config.diagram_bar_height / 2, y + config.diagram_bar_height, self.getDescriptionString(), str(self))

        return strResult


    def toFreemindNode(self):

        """  """

        strResult = self.getDescriptionFreemind()
        # TODO: handle color properties (s. Unit)

        return strResult


    def to_ical(self,cal):

        """  """

        if self.dt is not None and type(self.dt) is datetime:
            event = Event()

            event.add('summary', self.getDescriptionString())

            if type(self.dt) is datetime:
                event.add('dtstart', self.dt.date())
                event.add('dtend', self.dt.date() + timedelta(days=1))
            else:
                event.add('dtstart', self.dt)
                event.add('dtend', self.dt + timedelta(days=1))
                
            event.add('dtstamp', datetime.now().astimezone(None))
            cal.add_component(event)


if __name__ == '__main__':

    print('Module Test: ' + __file__ + '\n')
    
    t = Note('TEST').appendDescription('First Test')
    t.setDate(date(2023,11,22))

    print(t)
