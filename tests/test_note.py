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

from datetime import timedelta, date, datetime, time, timezone

from training.note import Note

print('Module Test: ' + __file__ + '\n')

t = Note()
print(t)

t = Note(['TEST','AAA'])
t.setDateStr('2020-04-04')
print(t)

t1 = t.dup()
print(t1)

t.parse('TEST, TTT')
t.setClock(time(8,15,0))
t.setDate(date(2025,1,1))
print(t)

#print(t.toXML())

