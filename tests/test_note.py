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

import sys

from datetime import timedelta, date, datetime, time, timezone

from training.note import Note

print('Module Test: ' + __file__ + '\n')

t = Note()
print(t)

t.setDateStr('2020-04-04')
t.appendDescription(['TEST','AAA & "BBB"'])
print(t.toString())

t1 = t.dup()
print(t1.getDescriptionHTML())

t2 = Note('2020-04-06;TEST, TTT')
t2.setDate(datetime(2025, 1, 7, 22, 0).astimezone(None))
#t.setClock(time(8,15,0))
#t.setDate(date(2025,1,1))
#t.setDate(True)
print(t2)

#print(t.toXML())

