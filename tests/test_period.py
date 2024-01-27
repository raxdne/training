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

from datetime import date

from training.note import Note
from training.unit import Unit
from training.cycle import Cycle
from training.period import Period

print('Module Test: ' + __file__ + '\n')

t = Period('General Basics',30)
t.appendDescription('Regeneration')

t.append(Note('ABC'))

#t.define(['3000;Bicycle;100h','100;Running;'])
#t.define(['2000;Bicycle;','100;Running;'])
#t.define(';Bicycle;100h')
#t.schedule(2025,3,4)
#print(t.report())
#

#t = Period('General Basics',60).define(['2000;Bicycle;','100;Running;']).schedule(2025,3,4)
#print(t.getNumberOfCycles())
#print(t.getTitleString())

#print(t.toString())
#print(t.toHtml())

c = Cycle('General Endurance')
c.insert(1,Unit('18:00;3.5;RB;25:00;;http://www.demo.com/'))
c.insert(3,Unit('18:00;3.5;RB;25:00'))
c.insert(5,Unit(';FB;25:00'))
c.insert(6,Unit('08:00;30;BB;02:00:00'))

t.append(c)
t.append(c)
c.scale(1.2,r"FB")
t.append(c)
t.append(c)
t.append(c)

# c.appendDescription('Nutrition ABC')
# f.appendDescription('Maximum')

#t.append(c)
# t.append(c)
# f.setDescription()
# t.append(c)

#t.fix(Date(2025,3,4))
t.schedule(2025)
#t.cut(140)
#t.cut(date(2025,1,25))
t.insert(Note('2025-01-07;;;;NOTE'))

print(t)
#print(t.report())
#print(t.toHtml())
#print(t.toXML())
#print(t.toVCalendar())
#print(t.toSVG())
#print(t.toSVGGanttChart())

#quit()

#t = Period('Plan').CalendarWeekPeriod(2022)
#t = Period('Plan').CalendarYearPeriod(2023)
#t = Period('Report').CalendarLastWeeksPeriod(4)
#t = Period('Plan').CalendarSeasonPeriod(2025)
#t.insertByDate(Unit('2025-03-03T8:00:00+2;100;RG;5h'))
#t1 = t.getPeriodByDate()
#t1 = t.getCycleByDate()

#print(t1)
#print(t.report())
