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

from training.note import Note
from training.unit import Unit
from training.pause import Pause
from training.combination import Combination
from training.cycle import Cycle
import training.config as config

from suntime import Sun

# location Berlin/Germany
config.sun = Sun(52.5,13.5)
config.twilight = 1800

print('Module Test: ' + __file__ + '\n')

t = Cycle('C1',2*7)

c = Combination([Unit('18:00;3.5;RB;25:00'),
                 Pause('20min'),
                 Unit('18:00;3.5;RB;25:00')])
c.appendDescription('Running Blocks')
c1 = c.dup()
#c1.scale(2.0,r"^R")

#t.insert(1,Unit('18:00;3.5;RB;25:00'))
#t.insert(3,[Unit('08:00;3.5;RB;25:00'),
#            Unit('18:00;3.5;RB;25:00')])
t.insert([5,8],c)
#t.insert(6,Unit('06:00;30;BB;02:00:00'))
#t.insert(8,Unit(';FB;25:00'))
#t.insert(10,Unit(';FB;25:00'))
#t.insert(13,Unit('08:00;30;BB;02:00:00'))

t.schedule(2023,1,1)

#t.insertByDate(Unit('2023-03-03T8:00:00+2;100;RG;5h'), True)
#t.resetDistances()

#print(t)

#t.scale(2.0)
#print(t)

#print(t.toHtml())
#print(t.toSVG())
#print(t.toSVGDiagram())
#print(t.toSVGGanttChart())
print(t.toFreeMind())
#print(t.toXML())

#print(t.report())
