#
#
#

#import pdb

import sys

from datetime import date

from training.unit import Unit
from training.cycle import Cycle
from training.period import Period
import training.config as config


def RegenerationGeneral():
    r = Cycle('General Regeneration')
    r.insert(1,Unit(';Bicycle;1:15:00'))
    r.insert(3,Unit(';Running;25:00'))
    r.insert(6,Unit(';Bicycle;1:15:00'))

    return r


def BasicsGeneral():
    p = Period('General Basics')
    p.appendDescription('Regeneration')

    c = Cycle('General Endurance')
    c.insert(1,Unit(';Running;45min'))
    c.copy(1,3)
    c.insert(5,Unit(';Strength;30min'))
    c.insert(6,Unit(';Bicycle;1h'))

    p.append(c)
    #c.remove(intIndexA=-1,patternType=r'^[R]')
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())
    p.append(c)
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())
    p.append(c)
    
    return p


def BasicsBicycle():
    p = Period('Basics Endurance Bicycle')
    p.appendDescription('Weight, Metabolism, Nutrition')
    p.appendDescription('1000 km, switch to Racing bike')
    
    c = Cycle('Focus Bicycle')
    c.insert(1,Unit('30;Bicycle;1:15:00'))
    c.insert(3,Unit('3.5;Running;25:00'))
    c.insert(3,Unit(';Strength;25:00'))
    c.insert(6,Unit('40;Bicycle;02:00:00'))

    p.append(c)
    p.append(c)
    p.append(c)
    p.appendChildDescription('Test 5km Time trial')
    p.append(RegenerationGeneral())
    p.append(c)
    c.scale(1.2)
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())

    return p


def BuildupBicycleSpeed():
    p = Period('Buildup Bicycle Speed')
    p.appendDescription('Sprint Final speed')

    c = Cycle('Focus Bicycle Speed')
    c.insert(1,Unit('30;Bicycle;1:15:00'))
    c.insert(3,Unit('3.5;Running;25:00'))
    c.insert(3,Unit(';Strength;25:00'))
    c.insert(5,Unit(';Strength;25:00'))
    c.insert(6,Unit('40;Bicycle;02:00:00'))

    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())
    p.append(c)
    
    return p


def HighlightBicycle1():
    c = Cycle('Highlight Bicycle Distance')
    
    h = Unit('100;Bicycle;5:00:00')
    h.appendDescription('Bicycle about 100 km')
    
    c.insert(1,Unit('30;Bicycle;25:00'))
    c.insert(3,Unit('3.5;Running;25:00'))
    c.insert(6,h)

    return c


def BicycleSimple():
    p = Period('Bicycle')
    
    p.append(BasicsBicycle())
    p.append(BuildupBicycleSpeed())
    p.append(Period('Buildup Bicycle Speed',21))
    p.append(BasicsBicycle())
    p.append(BuildupBicycleSpeed())

    return p


def BasicsRunning():
    p = Period('Specific Basics Running')
    p.appendDescription('Change of Focus')

    c = Cycle('Focus Running')
    c.insert(2,Unit('3.5;Running;25:00'))
    c.insert(3,Unit(';Strength;25:00'))
    c.insert(4,Unit('3.5;Running;02:30:00'))
    c.insert(6,Unit('30;Bicycle;1:25:00'))
    
    p.append(c)
    p.append(c)
    p.appendChildDescription('Test 1000m speed run')
    p.append(RegenerationGeneral())
    c.scale(1.2)
    p.append(c)
    p.append(c)
    p.appendChildDescription('Test 1000m speed run')
    p.append(RegenerationGeneral())

    return p


def BuildupRunningSpeed():
    p = Period('Buildup Running Speed')
    
    c = Cycle('Focus Running')
    c.appendDescription('Test 1000m speed run')
    c.insert(1,Unit('30;Bicycle;1:25:00'))
    c.insert(3,Unit('5;Bicycle;25:00'))
    c.insert(3,Unit(';Strength;25:00'))
    c.insert(6,Unit('5;Bicycle;02:30:00'))
    
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())

    return p

def HighlightRunning1():
    c = Cycle('Highlight Running Distance')

    h = Unit('10;Running;1:00:00')
    h.appendDescription('Running min. 10 km')
    c.insert(6,h)
    
    return c


def RunningSimple():
    p = Period('Running')
    p.appendDescription('Compensation swimming')
    
    p.append(BasicsRunning())
    p.append(HighlightRunning1())
    p.append(Cycle('Highlight Running Distance',14))
    p.append(BuildupRunningSpeed())
    p.append(BuildupRunningSpeed())
    p.append(HighlightRunning1())

    return p




def PlanSimple(strArg):

    s = Period(strArg)
    s.appendDescription(['Targets', [['Same volume like last season'],['defined Highlights',['Bicycle','Run']]]])
    s.appendDescription(['Rules',[['Regeneration'],['Differenciation',['Type','Intensity','Distance']]]])

    s.append(BasicsGeneral())
    #s.append(BasicsAlternative())
    s.append(BicycleSimple())
    #s.append(RegenerationGeneral())
    s.append(RunningSimple())

    #s.resetUnits()
    #s.parseFile('Training{}.csv'.format(date.today().year))

    return s


#print(config.getSettingsStr())

s = PlanSimple('Season Simple').schedule(date.today().year,1,1).updateValues()
#s.updateValues({'Running': 6.0, 'Bicycle': 20.0})

# patch some days using a scheduled cycle
c = Cycle('Pause Running').insert([1,3,5],Unit('10;Running;3:00:00')).schedule(date.today().year,7,2)
print('info: ' + str(c), file=sys.stderr)
#breakpoint()
s.insertByDate(c,True)
    
#s.remove(patternType=r'^[^B]')

print(s.report())

f = open('SimplePlanGantt.svg', encoding='utf-8', mode='w')
f.write(s.toSVGGanttChart())
f.close()

f = open('SimplePlan.svg', encoding='utf-8', mode='w')
f.write(s.toSVGDiagram())
f.close()

f = open('SimplePlan.mm', encoding='utf-8', mode='w')
f.write(s.toFreeMind())
f.close()

f = open('SimplePlan.ics', 'wb')
f.write(s.toVCalendar())
f.close()

f = open('SimplePlan.txt', encoding='utf-8', mode='w')
f.write(s.toString())
f.close()

f = open('SimplePlan.csv', encoding='utf-8', mode='w')
f.write(s.toCSV())
f.close()

f = open('SimplePlan.html', encoding='utf-8', mode='w')
f.write(s.toHtmlFile())
f.close()

