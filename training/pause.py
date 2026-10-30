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

class Pause(TItem):

    """ class for training pauses """

    def __init__(self,d=None,t=None):

        """  """

        super().__init__(t)
        self.d = d


    def __repr__(self):

        strResult = f'{self.__class__.__name__}([{self.dt!r},{self._d!r}])'
        if self.hasDescription():
            strResult += f'.appendDescription({self.description!r})'

        return strResult


    def __str__(self):

        """  """

        if self.d.total_seconds() > 0:
            if self.hasDescription():
                return f'{super().getDescriptionString()} {self.d.toString()}'
            else:
                return f'Pause {self.d.toString()}'
        else:
            return ''


    def set(self,**kwargs):
        
        """ generic setter """
        
        for key, value in kwargs.items():
            if key in ['dt','description','d']:
                setattr(self, key, value)

        return self


    def scale(self,f,p=None):

        """ returns a scaled copy of self """

        r = self.dup()
        if f > 0.01 and  abs(f - 1.0) > 0.01 and (p is None or r.type is None or re.match(p,r.type)):
            r.d = r.d.scale(f)

        return r


    def toStringShort(self):

        """  """

        strResult = ''

        if self.d.total_seconds() > 0:
            strResult =  f'Pause {self.d.toString()}'

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
        
        return self.d


    def stat(self, skipType=None):

        """  """
        
        return self


    def parse(self,o):

        """  """
        
        if o is None or not o:
            return False
        elif type(o) is str:
            self.color = "#ffff00"
            entry = o.split(';')
            #print('Note {}'.format(str(entry)), file=sys.stderr)
            if len(entry) == 1:
                self.appendDescription(o)
                return True
            elif len(entry) == 2:
                self.setDateStr(entry[0])
                self.appendDescription(entry[1:])
                return True
            else:
                return self.parse(entry)
        elif type(o) is list and len(o) > 3:
            if o[0] and not o[1] and not o[2] and not o[3]:
                self.setDateStr(o[0])
                self.appendDescription(o[4:])
                #print('Note {}'.format(str(self)), file=sys.stderr)
                return True
            else:
                return False
        else:
            return False


    def toCSV(self):

        """  """

        strResult = ''

        return strResult


    def toHtmlTable(self):

        """  """

        strResult = ''

        if self.d.total_seconds() > 0:
            strResult =  f'<div {config.getClass(__name__)} style="background-color: {self.color}">{str(self)}</div>'

        return strResult


    def toSVG(self,x,y):

        """  """

        strResult = ''

        if self.d.total_seconds() < 60:
            strResult += '<text x="{}" y="{}">{}<title>{}</title></text>\n'.format(x + config.diagram_bar_height / 2, y + config.diagram_bar_height, self.getDescriptionString(), str(self))
        else:
            strResult += '<rect '

            # "about 25 distance units per hour"
            bar_width = self.d.total_seconds() / 3600 * 25 * config.diagram_scale_dist

            strResult += ' height="{}" opacity=".25" stroke="black" stroke-width=".5" width="{:.0f}" x="{}" y="{}"'.format(config.diagram_bar_height, bar_width, x, y)
            strResult += '>'

            strResult += '<title>{}</title>'.format(self)

            strResult += '</rect>\n'

        return strResult


    def toFreemindNode(self):

        """  """

        strResult = '<node TEXT="' + self.toStringShort() + '">'

        strResult += '</node>\n'

        return strResult


    def to_ical(self,cal):

        """  """

    def toSqlite(self):

        """  """

        strResult = ''

        return strResult


if __name__ == '__main__':

    print('Module Test: ' + __file__ + '\n')
    
    t = Pause(11,'TEST').appendDescription('First Test')
    t.setDate(datetime(2023,11,22,12,9,11))
    t.d = 22

    print(t)
