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

from datetime import timedelta, date, datetime, time, timezone

from training.description import Description
from training.title import Title
from training.note import Note
from training.unit import Unit
from training.cycle import Cycle
from training.period import Period
import training.config as config

from suntime import Sun

# location Berlin/Germany
config.sun = Sun(52.5,13.5)
config.twilight = 1800

print('Module Test: ' + __file__ + '\n')

t = Period('Suntime')

c = Cycle('Sun',365)

for d in range(0,len(c)):
    c.insert(d,[Unit('sr;5;Running;30min;Sunrise'),
                Unit('ss;5;Running;30min;Sunset')])

t.append(c)
t.schedule(2023,1,1)
print(t)

