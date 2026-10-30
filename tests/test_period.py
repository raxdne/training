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

from datetime import date, datetime, timedelta

from training.note import Note
from training.unit import Unit
from training.cycle import Cycle
from training.bunch import Bunch
from training.period import Period

print('Module Test: ' + __file__ + '\n')

t = Period('Plan')
#t.appendDescription('Regeneration')

b = Bunch('General Endurance',2*7).append([Bunch('General Endurance',3*7),Bunch('Endurance'),'Test ABC'])
b.extend()

c1 = Cycle('Specific Endurance A')
c2 = Cycle('Specific Endurance B')
c = Cycle('Specific Endurance C').append([c1,c2]).extend()

#t.append([Period('General Basics I',36).append(Cycle('General Endurance',24)),c,Period('General Basics II',36).append([Period('General Basics IIa',36),c.scale(2),Period('General Basics IIb',36)]),Period('General Basics III',36)])

u = Period('Sub-Plan')
for i in range(5):
    u.append(Period(f'P{i}').append([b,c,c,b,c,c]))

for i in range(5):
    t.append(u)

t.schedule(date(2025,1,1))
#t.cutAfter(date(2026,1,1))
#t.cutBefore(date(2025,11,1))

print(t)

#t.ins(b,date=date(2025,2,1))
#t.ins(c,date=date(2025,4,1))

#t.ins([c,b,c,b],date=date(2025,6,1))

#t.qy()
        
#for i in t.qy(index=[0,2,3]):
#    print(i.title + ' ' + i.getDateString())

#for i in t.qy(date=datetime(2025,2,1),type=Cycle,level=10):
#    print(i.title + ' ' + i.getDateString())

#t.query(type=Period,level=1)
#t.query(type=Period,date=datetime(2025,2,1),level=2)

#t.query(date=datetime(2025,2,1))
#t.query(type=Period,date=datetime(2025,2,1))
#t.query(type=Cycle,date=datetime(2025,1,14),level=5)
#t.query(type=Cycle,date=datetime(2025,2,1),level=2)

#t.query(index=1)
#t.query(index=[1,3])

#t.query(path=[1,3])

#t.schedule(date.today())
#t.setTextOnly(False)
#t.setPlot()

#print(t)
#print(t.report())

#print(t.toXML())
#print(t.toVCalendar())
#print(t.toSVG())
#print(t.toSVGGanttChart())

#t = Period.CalendarMonthPeriod(2029,'TEST')

f = open('Output/test_period.html','w')
f.write(t.toHtmlFile())
f.close()

f = open('Output/test_period.mm','w')
f.write(t.toFreeMind())
f.close()

