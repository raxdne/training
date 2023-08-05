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

    def __new__(cls,objArg):

        """  """

        intMin = 0
        
        if objArg == None:
            pass
        elif type(objArg) is int:
            intMin = objArg
        elif type(objArg) is str:
            entry = objArg.split(':')
            if len(entry) == 1:
                # nothing to split
                entry = objArg.split('min')
                if len(entry) == 2:
                    intMin = int(entry[0])
                else:
                    entry = objArg.split('h')
                    if len(entry) == 2:
                        intMin = int(float(entry[0]) * 60.0)
            elif len(entry) == 2:
                intMin = int(entry[0]) + int(entry[1]) / 60.0
            elif len(entry) == 3:
                intMin = int(float(entry[0]) * 60.0) + int(entry[1]) + int(entry[2]) / 60
            
        return super().__new__(cls,minutes=intMin)

    
    def __str__(self):

        """  """

        seconds = super().total_seconds()
        
        if seconds > 0:        
            strResult = '{:02}:{:02}:{:02}'.format(int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60))
        else:
            strResult = ''
            
        return strResult


    def __deepcopy__(self,memo):

        """  """

        return super().__new__(Duration,seconds=self.total_seconds())


    def scale(self,floatScale):

        """  """

        s = self.total_seconds()
        if s < 900.0:
            return super().__new__(Duration,seconds=s * floatScale)
        else:
            # round duration to 5:00 min
            return super().__new__(Duration,seconds=(round(s * floatScale / 300.0) * 300.0))
