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

#
#
#

class Title:

    """ abstract class to handle title """

    def __init__(self,strArg=None):

        """  """

        self.setTitleStr(strArg)


    def __str__(self):

        """  """

        return self.strTitle


    def setTitleStr(self,strArg):

        """  """

        if strArg == None:
            self.strTitle = '-'
        else:
            self.strTitle = strArg

        return self

    
    def hasTitle(self):

        """  """

        return self.strTitle != None and len(self.strTitle) > 0


    def getTitleStr(self):

        """  """

        return self.strTitle
        #return str(self)


