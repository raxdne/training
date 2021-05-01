
from datetime import (
    timedelta,
    date,
    datetime,
    time
)

from training import training


def RegenerationGeneral():
    r = training.cycle('General Regeneration')
    r.insert(1,training.unit('30;BR;1:15:00'))
    r.insert(3,training.unit('3.5;RR;25:00'))
    r.insert(6,training.unit('30;BR;1:15:00'))

    return r


def BasicsGeneral():
    p = training.period('General Basics')
    p.appendDescription('Regeneration')

    c = training.cycle('General Endurance')
    c.insert(1,training.unit('3.5;RB;25:00'))
    c.insert(3,training.unit('3.5;RB;25:00'))
    f = c.insert(4,training.unit(';FB;25:00'))
    c.insert(5,training.unit(';FB;25:00'))
    c.insert(6,training.unit('30;BB;02:00:00'))

    p.append(c)
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())

    c.appendDescription('Nutrition ABC')
    f.appendDescription('Maximum')
    
    p.append(c)
    p.append(c)
    f.setDescription()
    p.append(c)
    p.append(RegenerationGeneral())
    
    return p


def BasicsAlternative():
    p = BasicsGeneral()
    p.setTitleStr('Alternative Basics')
    p.scale(1.2)
    p.appendDescription('Extension')
    
    return p


def BasicsBicycle():
    p = training.period('Basics Endurance Bicycle')
    p.appendDescription('Weight, Metabolism, Nutrition')
    p.appendDescription('1000 km, switch to Racing bike')
    
    c = training.cycle('Focus Bicycle')
    c.insert(1,training.unit('14:00;30;BB;1:15:00'))
    c.insert(3,training.unit('17:15;3.5;RR;25:00'))
    c.insert(3,training.unit(';FB;25:00'))
    c.insert(6,training.unit('16:00;40;BB;02:00:00'))

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
    c.insert(1,training.unit('30;BI;1:15:00'))
    c.insert(3,training.unit('3.5;RR;25:00'))
    c.insert(3,training.unit(';FB;25:00'))
    c.insert(5,training.unit(';FB;25:00'))
    c.insert(6,training.unit('40;BI;02:00:00'))

    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())
    p.append(c)
    
    return p


def HighlightBicycle1():
    c = training.cycle('Highlight Bicycle Distance')
    
    h = training.unit('100;BB;5:00:00')
    h.appendDescription('Bicycle about 100 km')
    
    c.insert(1,training.unit('30;BR;25:00'))
    c.insert(3,training.unit('3.5;RR;25:00'))
    c.insert(6,h)

    return c


def BuildupBicycleForce():
    p = training.period('Buildup Bicycle Force')
    p.appendDescription('Force uphill')

    c = training.cycle('Focus Bicycle Force')
    c.insert(1,training.unit('30;BI;1:15:00'))
    c.insert(3,training.unit('3.5;RR;25:00'))
    c.insert(3,training.unit(';FB;25:00'))
    c.insert(5,training.unit(';FB;25:00'))
    c.insert(6,training.unit('40;BI;02:00:00'))

    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())
    p.append(c)
    
    return p


def HighlightBicycle2():
    c = training.cycle('Highlight Bicycle Mountain')

    h = training.unit('60;BI;03:00:00')
    h.appendDescription('Mountain')
    
    c.insert(1,training.unit('30;BR;1:15:00'))
    c.insert(3,training.unit(';FB;25:00'))
    c.insert(6,h)

    return c


def BuildupBicycleSpeed():
    p = training.period('Buildup Bicycle Speed')
    p.appendDescription('Speed Trime Trial')

    c = training.cycle('Focus Bicycle Speed')
    c.insert(1,training.unit('30;BI;1:15:00'))
    c.insert(3,training.unit('3.5;RR;25:00'))
    c.insert(3,training.unit(';FB;25:00'))
    c.insert(6,training.unit('40;BI;02:00:00'))

    p.append(c)
    p.append(c)
    p.appendChildDescription('Test 5km Trime Trial')
    p.append(RegenerationGeneral())
    p.append(c)
    p.append(c)
    p.appendChildDescription('Test 5km Trime Trial')
    p.append(RegenerationGeneral())
    
    return p


def HighlightBicycle3():
    c = training.cycle('Highlight Bicycle Trime Trial')

    h = training.unit('20;BI;40:00')
    h.appendDescription('Trime Trial')
    
    c.insert(1,training.unit('30;BR;1:15:00'))
    c.insert(3,training.unit(';FB;25:00'))
    c.insert(6,h)

    return c


def Bicycle2021():
    p = training.period('Bicycle')
    
    p.append(BasicsBicycle())
    p.append(BuildupBicycleSpeed())
    p.append(BuildupBicycleForce())
    p.append(training.period('Buildup Bicycle Speed',21))
    p.append(HighlightBicycle2())
    p.append(BuildupBicycleSpeed())
    p.append(HighlightBicycle3())

    return p


def BasicsRunning():
    p = training.period('Specific Basics Running')
    p.appendDescription('Change of Focus')

    c = training.cycle('Focus Running')
    c.insert(2,training.unit('3.5;RB;25:00'))
    c.insert(3,training.unit(';FB;25:00'))
    c.insert(4,training.unit('3.5;RB;02:30:00'))
    c.insert(6,training.unit('30;BR;1:25:00'))
    
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
    c.insert(1,training.unit('30;BR;1:25:00'))
    c.insert(3,training.unit('5;BI;25:00'))
    c.insert(3,training.unit(';FB;25:00'))
    c.insert(6,training.unit('5;BI;02:30:00'))
    
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())

    return p


def BuildupRunningSpeed():
    p = training.period('Buildup Running Speed')
    
    c = training.cycle('Focus Running')
    c.appendDescription('Test 1000m speed run')
    c.insert(1,training.unit('30;BR;1:25:00'))
    c.insert(3,training.unit('5;BI;25:00'))
    c.insertDescriptionStr(3,'Test 3 x 1000m speed run')
    c.insert(3,training.unit(';FB;25:00'))
    c.insert(6,training.unit('5;BI;02:30:00'))
    
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())

    return p


def HighlightRunning1():
    c = training.cycle('Highlight Running Distance')

    h = training.unit('10;RB;1:00:00')
    h.appendDescription('Running min. 10 km')
    c.insert(6,h)
    
    return c


def HighlightRunning2():
    c = training.cycle('Highlight Running Competition',1)

    h = training.unit('6.5;RC;35:00')
    h.appendDescription('High Mountain Uphill Run')
    c.insert(0,h)
    
    return c


def Running2021():
    p = training.period('Running')
    p.appendDescription('Compensation swimming')
    
    p.append(BasicsRunning())
    p.append(HighlightRunning1())
    p.append(training.cycle('Highlight Running Distance',14))
    p.append(BuildupRunningSpeed())
    p.append(BuildupRunningSpeed())
    p.append(HighlightRunning2())

    return p




def Plan2021(strArg):

    s = training.period(strArg)
    s.appendDescription(['Targets', [['Same volume like last season'],['defined Highlights',['Bicycle','Run']]]])
    s.appendDescription(['Rules',[['Regeneration'],['Differenciation',['Type','Intensity','Distance']]]])
    s.appendDescription(['Units',[['Bicycle',['BB - Basics','BI - Intensity','BS - Speed','BC - Compensation']],['Run',['RB - Basics','RI - Intensity','RS - Speed','RC - Compensation']],['Strength, Force',['FB - Basics','FI - Intensity','FS - Speed']],['Competition',['Bicycle','Run']]]])

    s.append(BasicsGeneral())
    #s.append(BasicsAlternative())
    s.append(Bicycle2021())
    #s.append(RegenerationGeneral())
    s.append(Running2021())

    s.schedule(2021,1,4)

    #s.resetUnits()
    #s.parseFile('Training2021.csv')

    return s



s = Plan2021('Season 2021')

#print(s.report())
print(s.stat())

f = open('Plan2021.mm', 'w')
f.write(s.toFreeMind())
f.close()

f = open('Plan2021.ics', 'w')
f.write(s.toVCalendar())
f.close()

f = open('Plan2021.txt', 'w')
f.write(s.toString())
f.close()

f = open('Plan2021.csv', 'w')
f.write(s.toCSV())
f.close()

