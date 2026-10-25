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

from datetime import timedelta

#
#
#

class Duration(timedelta):

    """ extension class for timedelta (https://stackoverflow.com/questions/48461081/cant-inherit-from-timedelta) """

    def __new__(cls,o):

        """  """

        intMin = 0
        
        if o == None:
            pass
        elif isinstance(o,timedelta):
            intMin = round(o.total_seconds() / 60.0)
        elif type(o) is float:
            intMin = round(o)
        elif type(o) is int:
            intMin = o
        elif type(o) is str:
            entry = o.split(':')
            if len(entry) == 1:
                # nothing to split
                entry = o.split('min')
                if len(entry) == 2:
                    intMin = round(float(entry[0]))
                else:
                    entry = o.split('h')
                    if len(entry) == 2:
                        intMin = round(float(entry[0]) * 60.0)
            elif len(entry) == 2:
                intMin = int(entry[0]) + round(int(entry[1]) / 60.0)
            elif len(entry) == 3:
                intMin = int(entry[0]) * 60.0 + int(entry[1]) + int(entry[2]) / 60
            
        return super().__new__(cls,minutes=intMin)

    
    def __str__(self):

        """  """

        seconds = super().total_seconds()
        hour, remainder = divmod(seconds, 3600)
        min, sec = divmod(remainder, 60)
        
        return f'{hour:02.0f}:{min:02.0f}:{sec:02.0f}'


    def toString(self):

        """  """

        seconds = super().total_seconds()
        hour, remainder = divmod(seconds, 3600)
        min, sec = divmod(remainder, 60)

        if seconds > 3599:        
            strResult = f'{hour:.0f}:{min:02.0f} h'
        elif seconds > 900:        
            strResult = f'{min:.0f} min'
        elif seconds > 30:        
            strResult = f'{min:.0f}:{sec:02.0f} min'
        elif seconds > 0:        
            strResult = f'{sec:.0f} s'
        else:
            strResult = '-:--'

        return strResult


    def __deepcopy__(self,memo):

        """  """

        return super().__new__(Duration,seconds=self.total_seconds())


    def scale(self,f):

        """  """

        if f > 0.01 and  abs(f - 1.0) > 0.01:
            s = self.total_seconds()
            if s < 1800.0:
                return super().__new__(Duration,seconds=round(s * f))
            elif s < 3600.0:
                return super().__new__(Duration,seconds=round(s * f / 60.0) * 60.0)
            else:
                # round duration to 5:00 min
                return super().__new__(Duration,seconds=round(s * f / 300.0) * 300.0)
