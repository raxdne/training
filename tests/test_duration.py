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

import copy

from training.duration import Duration

print('Module Test: ' + __file__ + '\n')

t = Duration(10)
print(repr(t))
print(t)

t1 = copy.deepcopy(t)
print(repr(t1))
print(t1)

t = Duration('3:30')
print(repr(t))
print(t)

t = Duration('30min')
print(repr(t))
print(t)

t = Duration('3h')
print(repr(t))
print(t)

