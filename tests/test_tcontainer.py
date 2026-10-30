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

from training.tcontainer import TContainer

#
#
#

class Dummy(TContainer):

    """ class for Testing only """

    def __init__(self,t=None):

        """  """

        super().__init__(t)


    def getLength(self):

        """ return calculated length """

        pass


    def getDuration(self, skipType=None):

        """ return a timedelta """

        pass


    def append(self,o):

        """ append objects to the list of childs """

        pass


    def cutBefore(self,d):

        """  """

        pass


    def cutAfter(self,d):

        """  """

        pass


    def stat(self, dt0=None, dt1=None, skipType=None):

        """ stat all descendant data to self.data and returns it as a nested list  """

        pass


    def updateValues(self,dictArg=None):

        """  """

        pass


    def scale(self,f,p=None):

        """ returns a copy of self, scaled by f and matching pattern p if not None """

        pass


    def resetDistances(self):

        """  """

        pass


    def insertByDate(self,o,f=False):

        """  """

        pass


    def remove(self,p=None):

        """  """

        pass


    def toHtmlTable(self):

        """  """
        
        pass


print('Module Test: ' + __file__ + '\n')

t = Dummy('XYZ')
t.periodInt = 12
print(repr(t))
print(hasattr(t,'title'))
print(t)
