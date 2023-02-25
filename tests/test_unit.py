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

from training.unit import Unit

print('Module Test: ' + __file__ + '\n')

#t = Unit('2020-03-03T17:00:00+1:00;10;RG;20min')
t = Unit('10:00;10;R Basics;20min')
t.setDate(date(2025, 1, 7))
print(t)
t.scale(2)
print(t)

#t.setClock()
#print(t)
#t.setDate(datetime(2025, 1, 7).astimezone(None))
#t.setDate(datetime(2025, 1, 7, 22, 0).astimezone(None))
#t.setDate(datetime(2025, 1, 7).astimezone(None),datetime(2025, 1, 7, 8, 0).astimezone(None),datetime(2025, 1, 7, 20, 0).astimezone(None))
#t.setDate(datetime(2025, 1, 7, 2, 0).astimezone(None),datetime(2025, 1, 7, 8, 0).astimezone(None),datetime(2025, 1, 7, 20, 0).astimezone(None))
#t.setDate(datetime(2025, 1, 7, 22, 0).astimezone(None),datetime(2025, 1, 7, 8, 0).astimezone(None),datetime(2025, 1, 7, 20, 0).astimezone(None))
#t.setClock(time(0))
#t.setColor('#ffaaaa')
#print(t.toHtml())
#print(t.toXML())

#t = Unit('08:00;10;RG;20min')
#print(t)

#d = {}
#t.stat(d)
