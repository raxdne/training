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

from training.tcore import TCore

#
#
#

class Dummy(TCore):

    """ class for Testing only """

    def __init__(self,t=None):

        """  """

        super().__init__(t)



print('Module Test: ' + __file__ + '\n')

t = Dummy('XYZ')
print(repr(t))
print(t)

t1 = t.dup()
print(t1)

t = Dummy()
t.title = 'DEF GHI'
t.description = ['AAA',['BBB','CCC'],['DDD','EEE']]
t.description.extend(['WWW',['YYY','ZZZ','http://www.demo.org/']])

t.appendDescription('garmin:12345678')

print(t)

