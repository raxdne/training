
from datetime import (
    timedelta,
    date,
    datetime,
    time
)

from training import training


def RegenerationGeneral():
    r = training.cycle('General Regeneration')
    r.insert(1,training.unit('30;Cycling;1:15:00'))
    r.insert(3,training.unit('3.5;Running;25:00'))
    r.insert(6,training.unit('30;Cycling;1:15:00'))

    return r


def BasicsGeneral():
    p = training.period('General Basics')
    p.appendDescription('Regeneration')

    c = training.cycle('General Endurance')
    c.insert(1,training.unit('3.5;Running;25:00'))
    c.insert(3,training.unit('3.5;Running;25:00'))
    c.insert(5,training.unit(';Strength;25:00'))
    c.insert(6,training.unit('30;Cycling;02:00:00'))

    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())
    
    return p


def BasicsCycling():
    p = training.period('Basics Endurance Cycling')
    p.appendDescription('Weight, Metabolism, Nutrition')
    p.appendDescription('1000 km, switch to Racing bike')
    
    c = training.cycle('Focus Cycling')
    c.insert(1,training.unit('30;Cycling;1:15:00'))
    c.insert(3,training.unit('3.5;Running;25:00'))
    c.insert(3,training.unit(';Strength;25:00'))
    c.insert(6,training.unit('40;Cycling;02:00:00'))

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


def BasicsRunning():
    p = training.period('Specific Basics Running')
    p.appendDescription('Change of Focus')

    c = training.cycle('Focus Running')
    c.insert(2,training.unit('3.5;Running;25:00'))
    c.insert(3,training.unit(';Strength;25:00'))
    c.insert(4,training.unit('3.5;Running;02:30:00'))
    c.insert(6,training.unit('30;Cycling;1:25:00'))
    
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


def BasicsSwimming():
    p = training.period('Basics Endurance Swimming')
    
    c = training.cycle('Focus Swimming')
    c.insert(1,training.unit('2;Swimming;1:15:00'))
    c.insert(3,training.unit('3.5;Running;25:00'))
    c.insert(3,training.unit(';Strength;25:00'))
    c.insert(6,training.unit('3;Swimming;02:00:00'))

    p.append(c)
    p.append(c)
    p.appendChildDescription('Test 5km Time trial')
    p.append(RegenerationGeneral())
    p.append(c)
    c.scale(1.2)
    p.append(c)
    p.append(RegenerationGeneral())

    return p


def BasicsCombination():
    p = training.period('Basics Endurance Combination: Swimming + Cycling + Running')
    
    c = training.cycle('Focus Swimming')
    c.insert(1,training.unit('2;Swimming;1:15:00'))
    c.insert(3,training.unit('3.5;Running;25:00'))
    c.insert(3,training.unit(';Strength;25:00'))
    c.insert(6,training.unit('3;Swimming;02:00:00'))

    p.append(c)
    p.append(c)
    p.appendChildDescription('Test 5km Time trial')
    p.append(RegenerationGeneral())
    p.append(c)
    c.scale(1.2)
    p.append(c)
    p.append(RegenerationGeneral())

    return p


def Highlight1():
    c = training.cycle('Highlight Triathlon Olympic Distance')

    c.insert(6,training.unit('1.5;Swimming;1:00:00'))
    c.insert(6,training.unit('40;Cycling;1:40:00'))
    c.insert(6,training.unit('10;Running;1:30:00'))
    
    return c


def PlanTriathlon(strArg):

    s = training.period(strArg)
    s.appendDescription(['Targets', [['Same volume like last season'],['defined Highlights',['Cycling','Run']]]])
    s.appendDescription(['Rules',[['Regeneration'],['Differenciation',['Type','Intensity','Distance']]]])

    s.append(BasicsGeneral())
    s.append(BasicsSwimming())
    s.append(BasicsCycling())
    s.append(BasicsRunning())
    s.append(BasicsCombination())
    s.append(Highlight1())

    s.schedule(2021,3,1)

    #s.resetUnits()
    #s.parseFile('Training2021.csv')

    return s



s = PlanTriathlon('Season Triathlon Basics')

#print(s.report())
print(s.stat())

f = open('TriathlonPlan.svg', 'w')
f.write(s.toSVGDiagram())
f.close()

f = open('TriathlonPlan.mm', 'w')
f.write(s.toFreeMind())
f.close()

f = open('TriathlonPlan.ics', 'w')
f.write(s.toVCalendar())
f.close()

f = open('TriathlonPlan.txt', 'w')
f.write(s.toString())
f.close()

f = open('TriathlonPlan.csv', 'w')
f.write(s.toCSV())
f.close()

