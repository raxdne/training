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
from training.duration import Duration
from training.note import Note

#
#
#

class Pause(Note):

    """ class for training pauses """

    def __init__(self,strArg=None,objArg=None):

        """  """

        super().__init__()

        self.setDuration()

        if strArg != None:
            self.setDuration(strArg)
            if objArg != None:
                super().setDescription(objArg)

        #print('New Pause: ' + str(self), file=sys.stderr)

 
    def __str__(self):

        """  """

        if self.getDuration().total_seconds() > 0:
            return '{} {} Pause'.format(str(super().__str__()), str(self.getDuration()))
        else:
            return ''


    def setDuration(self,intArg=None):

        """  """

        if intArg == None:
            self.duration = Duration(0)
        else:
            self.duration = Duration(intArg)


    def getDuration(self):

        """  """
        
        if self.duration == None:
            return timedelta(seconds=0)
        else:
            return self.duration


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

        strResult = '<p>'
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

            # "about 25 distance units per hour"
            bar_width = self.getDuration().total_seconds() / 3600 * 25 * config.diagram_scale_dist

            strResult += ' height="{}" opacity=".25" stroke="black" stroke-width=".5" width="{:.0f}" x="{}" y="{}"'.format(config.diagram_bar_height, bar_width, x, y)
            strResult += '>'

            strResult += '<title>{}</title>'.format(self)

            strResult += '</rect>\n'

        return strResult


    def toXML(self):

        """  """

        strResult = '<node TEXT="' + str(self) + '">'

        strResult += '</node>\n'

        return strResult


    def to_ical(self,cal):

        """  """

