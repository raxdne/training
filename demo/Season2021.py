#
#
#

from training.note import Note
from training.unit import Unit
from training.pause import Pause
from training.combination import Combination
from training.cycle import Cycle
from training.period import Period
import training.config as config

from suntime import Sun

# location Berlin/Germany
config.sun = Sun(52.5,13.5)
config.twilight = 1800

config.colors = {'W': '#ff5555', 'B': '#ffdddd', 'R': '#ddffdd', 'F': '#aaaaff', 'S': '#ddddff'}
Unit_distance = 'mi'
#config.max_length_type = 1
#print(config.getSettingsStr())

def RegenerationGeneral():
    r = Cycle('General Regeneration')
    r.insert(1,Unit('30;BR;1:15:00'))
    r.insert(3,Unit('3.5;RR;25:00'))
    r.insert(6,Unit('30;BR;1:15:00'))

    return r


def BasicsGeneral():
    p = Period('General Basics')
    p.appendDescription('Regeneration')
    p.setColor('#eeeeee')

    c = Cycle('General Endurance')

    """    """
    
    c.insert([1,5],Combination([Unit('18:00;3.5;RB;25:00'),
                                Pause(10,'Stretching'),
                                Unit(';FB;25:00'),
                                Pause(2*60,'Rest'),
                                Unit(';FB;25:00')]))
             
    c.insert(3,Unit(';FB;25:00'))

    c.insert(6,[Unit('08:00;30;BB;02:00:00'),
                Unit('18:00;30;BB;02:00:00')])

    p.append(c)
    p.append(c)
    c.scale(1.2,r"^B")
    p.append(c)
    p.append(RegenerationGeneral())

    c.appendDescription('Nutrition ABC')
    #f.appendDescription('Maximum')
    
    p.append(c)
    p.append(Note(['XYZ',['111','222']]))
    p.append(c)
    #f.setDescription()
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
    p = Period('Basics Endurance Bicycle')
    p.appendDescription('Weight, Metabolism, Nutrition')
    p.appendDescription('1000 km, switch to Racing bike')
    
    c = Cycle('Focus Bicycle')
    c.insert(1,Unit('14:00;30;BB;1:15:00'))
    c.insert(3,Unit('17:15;3.5;RR;25:00'))
    c.insert(3,Unit(';FB;25:00'))
    c.insert(6,Unit('16:00;40;BB;02:00:00'))

    p.append(c)
    p.append(c)
    c.scale(1.2,r"BB")
    p.append(c)
    p.appendChildDescription('Test 5km Time trial')
    p.append(RegenerationGeneral())
    p.append(c)
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())
    c.scale(1.2)
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())

    return p


def BuildupBicycleSpeed():
    p = Period('Buildup Bicycle Speed')
    p.appendDescription('Sprint Final speed')

    c = Cycle('Focus Bicycle Speed')
    c.insert(1,Unit('30;BI;1:15:00'))
    c.insert(3,Unit('3.5;RR;25:00'))
    c.insert(3,Unit(';FB;25:00'))
    c.insert(5,Unit(';FB;25:00'))
    c.insert(6,Unit('40;BI;02:00:00'))

    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())
    p.append(c)
    
    return p


def HighlightBicycle1():
    c = Cycle('Highlight Bicycle Distance')
    
    h = Unit('100;BB;5:00:00')
    h.appendDescription('Bicycle about 100 km')
    
    c.insert(1,Unit('30;BR;25:00'))
    c.insert(3,Unit('3.5;RR;25:00'))
    c.insert(6,h)

    return c


def BuildupBicycleForce():
    p = Period('Buildup Bicycle Force')
    p.appendDescription('Force uphill')

    c = Cycle('Focus Bicycle Force')
    c.insert(1,Unit('30;BI;1:15:00'))
    c.insert(3,Unit('3.5;RR;25:00'))
    c.insert(3,Unit(';FB;25:00'))
    c.insert(5,Unit(';FB;25:00'))
    c.insert(6,Unit('40;BI;02:00:00'))

    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())
    p.append(c)
    
    return p


def HighlightBicycle2():
    c = Cycle('Highlight Bicycle Mountain')

    h = Unit('60;BI;03:00:00')
    h.appendDescription('Mountain')
    
    c.insert(1,Unit('30;BR;1:15:00'))
    c.insert(3,Unit(';FB;25:00'))
    c.insert(6,h)

    return c


def BuildupBicycleSpeed():
    p = Period('Buildup Bicycle Speed')
    p.appendDescription('Speed Trime Trial')

    c = Cycle('Focus Bicycle Speed')
    c.insert(1,Unit('30;BI;1:15:00'))
    c.insert(3,Unit('3.5;RR;25:00'))
    c.insert(3,Unit(';FB;25:00'))
    c.insert(6,Unit('40;BI;02:00:00'))

    p.append(c)
    p.append(c)
    p.appendChildDescription('Test 5km Trime Trial')
    p.append(RegenerationGeneral())
    p.append(c)
    #p.append(c)
    #p.appendChildDescription('Test 5km Trime Trial')
    p.append(RegenerationGeneral())
    
    return p


def HighlightBicycle3():
    c = Cycle('Highlight Bicycle Trime Trial')

    h = Unit('20;BI;40:00')
    h.appendDescription('Trime Trial')
    
    c.insert(1,Unit('30;BR;1:15:00'))
    c.insert(3,Unit(';FB;25:00'))
    c.insert(6,h)

    return c


def Bicycle2021():
    p = Period('Bicycle')
    
    p.append(BasicsBicycle())
    p.append(BuildupBicycleSpeed())
    p.append(BuildupBicycleForce())
    p.append(Period('Buildup Bicycle Speed',21))
    p.append(HighlightBicycle2())
    p.append(BuildupBicycleSpeed())
    p.append(HighlightBicycle3())

    return p


def BasicsRunning():
    p = Period('Specific Basics Running')
    p.appendDescription('Change of Focus')

    c = Cycle('Focus Running')
    c.insert(2,Unit('3.5;RB;25:00'))
    c.insert(3,Unit(';FB;25:00'))
    c.insert(4,Unit('3.5;RB;02:30:00'))
    c.insert(6,Unit('30;BR;1:25:00'))
    
    p.append(c)
    p.append(c)
    p.appendChildDescription('Test 1000m speed run')
    p.append(RegenerationGeneral())
    c.scale(1.2)
    p.append(c)
    #p.append(c)
    #p.appendChildDescription('Test 1000m speed run')
    p.append(RegenerationGeneral())

    return p


def BuildupRunningSpeed():
    p = Period('Buildup Running Speed')
    
    c = Cycle('Focus Running')
    c.appendDescription('Test 1000m speed run')
    c.insert(1,Unit('30;BR;1:25:00'))
    c.insert(3,Unit('5;BI;25:00'))
    c.insert(3,Unit(';FB;25:00'))
    c.insert(6,Unit('5;BI;02:30:00'))
    
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())

    return p


def BuildupRunningSpeed():
    p = Period('Buildup Running Speed')
    
    c = Cycle('Focus Running')
    c.appendDescription('Test 1000m speed run')
    c.insert(1,Unit('30;BR;1:25:00'))
    c.insert(3,Unit('5;BI;25:00'))
    c.insertDescriptionStr(3,'Test 3 x 1000m speed run')
    c.insert(3,Unit(';FB;25:00'))
    c.insert(6,Unit('5;BI;02:30:00'))
    
    p.append(c)
    p.append(c)
    p.append(RegenerationGeneral())

    return p


def HighlightRunning1():
    c = Cycle('Highlight Running Distance')

    h = Unit('10;RB;1:00:00')
    h.appendDescription('Running min. 10 km')
    c.insert(6,h)
    
    return c


def HighlightRunning2():
    c = Cycle('Highlight Running Competition',1)

    h = Unit('6.5;RC;35:00')
    h.appendDescription('High Mountain Uphill Run')
    c.insert(0,h)
    
    return c


def Running2021():
    p = Period('Running')
    p.appendDescription('Compensation swimming')
    
    p.append(BasicsRunning())
    p.append(HighlightRunning1())
    p.append(Cycle('Highlight Running Distance',14))
    p.append(BuildupRunningSpeed())
    p.append(BuildupRunningSpeed())
    p.append(HighlightRunning2())

    return p




def Plan2021(strArg):

    s = Period(strArg)
    s.appendDescription(['Targets', [['Same volume like last season'],['defined Highlights',['Bicycle','Run']]]])
    s.appendDescription(['Rules',[['Regeneration'],['Differenciation',['Type','Intensity','Distance']]]])
    s.appendDescription(['Units',[['Bicycle',['BB - Basics','BI - Intensity','BS - Speed','BC - Compensation']],['Run',['RB - Basics','RI - Intensity','RS - Speed','RC - Compensation']],['Strength, Force',['FB - Basics','FI - Intensity','FS - Speed']],['Competition',['Bicycle','Run']]]])

    s.append(BasicsGeneral())
    #s.append(BasicsAlternative())
    s.append(Bicycle2021())
    #s.append(RegenerationGeneral())
    s.append(Running2021())

    s.schedule(2021,1,4)
    
    #s.resetDistances()
    #s.parseFile('Training2021.csv')

    return s


s = Plan2021('Season 2021')

print(s.report())

f = open('Season2021Gantt.svg', 'w')
f.write(s.toSVGGanttChart())
f.close()

f = open('Season2021.svg', 'w')
f.write(s.toSVGDiagram())
f.close()

f = open('Season2021.mm', 'w')
f.write(s.toFreeMind())
f.close()

f = open('Season2021.ics', 'wb')
f.write(s.toVCalendar())
f.close()

f = open('Season2021.txt', 'w')
f.write(s.toString())
f.close()

f = open('Season2021.csv', 'w')
f.write(s.toCSV())
f.close()

f = open('Season2021.html', 'w')
f.write(s.toHtmlFile())
f.close()

