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

    """ class for standalone notes """

    def __repr__(self):

        strResult = f'{self.__class__.__name__}{self.title}({self.dt!r})'
        if self.hasDescription():
            strResult += f'.appendDescription({self.description!r})'

        return strResult


    def __str__(self):

        """  """

        if self.dt is None:
            strResult = ''
        elif type(self.dt) is date or self.dt.time() == time(0):
            strResult = self.dt.strftime("%Y-%m-%d")
        else:
            strResult = self.dt.strftime("%Y-%m-%d %H:%M:%S")
            
        strResult += self.title + ' ' + self.getDescriptionString()

        return strResult


    def set(self,**kwargs):
        
        """ generic setter """
        
        for key, value in kwargs.items():
            if key in ['dt','description','title']:
                setattr(self, key, value)

        return self


    def parse(self,o):

        """  """
        
        if o is None or not o:
            return False
        elif type(o) is str:
            entry = o.split(';')
            # TODO: test elements of entry
            if len(entry) == 1:
                # note only
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
        elif type(o) is list and len(o) > 3:
            self.setDateStr(o[0])
            self.appendDescription(o[4:])
            return True
        else:
            return False


    def scale(self,f,p=None):

        """ returns a copy of self """

        r = self.dup()

        return r


    def stat(self, skipType=None):

        """  """
        
        return self


    def toHtmlTable(self):

        """  """

        return f'<div {config.getClass(__name__)} style="background-color: {self.color}">{self.getTitleXML()}{self.getDescriptionString()}</div>'


    def toCSV(self):

        """  """

        return f'{self.dt.strftime("%Y-%m-%d")};;;;{self.title}{self.getDescriptionString()}\n'


    def toSVG(self,x,y):

        """  """

        return f'<text x="{x + config.diagram_bar_height / 2}" y="{y + config.diagram_bar_height}">{self.getDescriptionString()}<title>{str(self)}</title></text>\n'


    def toFreemindNode(self):

        """  """

        strResult = '<node FOLDED="true" LOCALIZED_STYLE_REF="default"'
        if self.color is not None:
            strResult += f' BACKGROUND_COLOR="{self.color}"'
        strResult += ' TEXT="' + self.getTitleXML() + '">'
        strResult += self.getDescriptionFreemind()
        strResult += '</node>'

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
