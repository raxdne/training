
from datetime import (
    timedelta,
    date,
    datetime,
    time
)

from training import training


def RegenerationGeneral():
    r = training.cycle('General Regeneration')
    r.insert(1,training.unit('30;Bicycle;1:15:00'))
    r.insert(3,training.unit('3.5;Running;25:00'))
    r.insert(6,training.unit('30;Bicycle;1:15:00'))

    return r


def BasicsGeneral():
    p = training.period('General Basics')
    p.appendDescription('Regeneration')

    c = training.cycle('General Endurance')
    c.insert(1,training.unit('3.5;Running;25:00'))
    c.insert(3,training.unit('3.5;Running;25:00'))
    c.insert(5,training.unit(';Strength;25:00'))
    c.insert(6,training.unit('30;Bicycle;02:00:00'))

    p.append(c)
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())
    p.append(c)
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())
    p.append(c)
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())
    
    return p


def BasicsBicycle():
    p = training.period('Basics Endurance Bicycle')
    p.appendDescription('Weight, Metabolism, Nutrition')
    p.appendDescription('1000 km, switch to Racing bike')
    
    c = training.cycle('Focus Bicycle')
    c.insert(1,training.unit('30;Bicycle;1:15:00'))
    c.insert(3,training.unit('3.5;Running;25:00'))
    c.insert(3,training.unit(';Strength;25:00'))
    c.insert(6,training.unit('40;Bicycle;02:00:00'))

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
    c.scale(1.2)
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())

    return p


def BuildupBicycleSpeed():
    p = training.period('Buildup Bicycle Speed')
    p.appendDescription('Sprint Final speed')

    c = training.cycle('Focus Bicycle Speed')
    c.insert(1,training.unit('30;Bicycle;1:15:00'))
    c.insert(3,training.unit('3.5;Running;25:00'))
    c.insert(3,training.unit(';Strength;25:00'))
    c.insert(5,training.unit(';Strength;25:00'))
    c.insert(6,training.unit('40;Bicycle;02:00:00'))

    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())
    p.append(c)
    
    return p


def HighlightBicycle1():
    c = training.cycle('Highlight Bicycle Distance')
    
    h = training.unit('100;Bicycle;5:00:00')
    h.appendDescription('Bicycle about 100 km')
    
    c.insert(1,training.unit('30;Bicycle;25:00'))
    c.insert(3,training.unit('3.5;Running;25:00'))
    c.insert(6,h)

    return c


def BicycleSimple():
    p = training.period('Bicycle')
    
    p.append(BasicsBicycle())
    p.append(BuildupBicycleSpeed())
    p.append(training.period('Buildup Bicycle Speed',21))
    p.append(BasicsBicycle())
    p.append(BuildupBicycleSpeed())

    return p


def BasicsRunning():
    p = training.period('Specific Basics Running')
    p.appendDescription('Change of Focus')

    c = training.cycle('Focus Running')
    c.insert(2,training.unit('3.5;Running;25:00'))
    c.insert(3,training.unit(';Strength;25:00'))
    c.insert(4,training.unit('3.5;Running;02:30:00'))
    c.insert(6,training.unit('30;Bicycle;1:25:00'))
    
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
    p = training.period('Buildup Running Speed')
    
    c = training.cycle('Focus Running')
    c.appendDescription('Test 1000m speed run')
    c.insert(1,training.unit('30;Bicycle;1:25:00'))
    c.insert(3,training.unit('5;Bicycle;25:00'))
    c.insert(3,training.unit(';Strength;25:00'))
    c.insert(6,training.unit('5;Bicycle;02:30:00'))
    
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())

    return p

def HighlightRunning1():
    c = training.cycle('Highlight Running Distance')

    h = training.unit('10;Running;1:00:00')
    h.appendDescription('Running min. 10 km')
    c.insert(6,h)
    
    return c


def RunningSimple():
    p = training.period('Running')
    p.appendDescription('Compensation swimming')
    
    p.append(BasicsRunning())
    p.append(HighlightRunning1())
    p.append(training.cycle('Highlight Running Distance',14))
    p.append(BuildupRunningSpeed())
    p.append(BuildupRunningSpeed())
    p.append(HighlightRunning1())

    return p




def PlanSimple(strArg):

    s = training.period(strArg)
    s.appendDescription(['Targets', [['Same volume like last season'],['defined Highlights',['Bicycle','Run']]]])
    s.appendDescription(['Rules',[['Regeneration'],['Differenciation',['Type','Intensity','Distance']]]])

    s.append(BasicsGeneral())
    #s.append(BasicsAlternative())
    s.append(BicycleSimple())
    #s.append(RegenerationGeneral())
    s.append(RunningSimple())

    s.schedule(2021,1,4)

    #s.resetUnits()
    #s.parseFile('Training2021.csv')

    return s



s = PlanSimple('Season Simple')

#print(s.report())
print(s.stat())

f = open('SimplePlan.mm', 'w')
f.write(s.toFreeMind())
f.close()

f = open('SimplePlan.ics', 'w')
f.write(s.toVCalendar())
f.close()

f = open('SimplePlan.txt', 'w')
f.write(s.toString())
f.close()

f = open('SimplePlan.csv', 'w')
f.write(s.toCSV())
f.close()

