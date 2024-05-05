#
#
#

import sys

from datetime import date, timedelta

from training.unit import Unit
from training.cycle import Cycle
from training.period import Period
import training.config as config


def RegenerationGeneral():

    if True:
        r = Period('General Regeneration',7).define([';Bicycle;2h',';Running;1h'])
    else:
       r = Cycle('General Regeneration')
       r.insert([1,6],Unit(';Bicycle;1h'))
       r.insert(3,Unit(';Running;30min'))

    return r.setColor('#eeeeee')


def BasicsGeneral():

    p = Period('General Basics',4*7).define([';Bicycle;5h',';Running;5h'])
    p.appendDescription(['General physical Basics',['Core','Flexibility','']])

    return p


def BasicsBicycle():
    
    p = Period('Basics Endurance Bicycle',6*7).define([';Bicycle;20h'])
    p.appendDescription('Weight, Metabolism, Nutrition')
    
    return p


def BuildupBicycleSpeed():

    p = Period('Buildup Bicycle Speed',3*7).define([';Bicycle;15h'])
    p.appendDescription('Sprint Final speed')
    
    return p


def HighlightBicycle1():
    c = Cycle('Highlight Bicycle Distance').setColor('#ffffaa')
    
    h = Unit('100;Bicycle;5:00:00')
    h.appendDescription('Bicycle about 100 km')
    
    c.insert(1,Unit('30;Bicycle;25:00'))
    c.insert(3,Unit('3.5;Running;25:00'))
    c.insert(6,h)

    return c


def BicycleSimple():
    p = Period('Bicycle')
    
    p.append(BasicsBicycle())
    p.append(RegenerationGeneral())
    p.append(BuildupBicycleSpeed())
    p.append(HighlightBicycle1())
    p.append(RegenerationGeneral())
    p.append(BasicsBicycle())
    p.append(RegenerationGeneral())
    p.append(BuildupBicycleSpeed())
    p.append(RegenerationGeneral())

    return p


def BasicsRunning():
    
    p = Period('Specific Basics Running',5*7).define([';Bicycle;8h',';Running;8h'])
    p.appendDescription('Change of Focus')

    return p


def BuildupRunningSpeed():

    p = Period('Buildup Running Speed',4*7).define([';Bicycle;8h',';Running;8h'])
    
    return p


def HighlightRunning1():

    c = Cycle('Highlight Running Distance').setColor('#ffffaa')

    h = Unit('10;Running;1:00:00')
    h.appendDescription('Running min. 10 km')
    c.insert(6,h)
    
    return c


def RunningSimple():
    
    p = Period('Running')
    p.appendDescription('Compensation swimming')
    
    p.append(BasicsRunning())
    p.append(HighlightRunning1())
    p.append(BuildupRunningSpeed())
    p.append(BuildupRunningSpeed())
    p.append(HighlightRunning1())

    return p


def PlanSimple(strArg):

    s = Period(strArg)
    s.appendDescription(['Targets', [['Same volume like last season'],['defined Highlights',['Bicycle','Run']]]])
    s.appendDescription(['Rules',[['Regeneration'],['Differenciation',['Type','Intensity','Distance']]]])

    s.append(BasicsGeneral())
    s.append(BicycleSimple())
    s.append(RunningSimple())
    s.append(Period('Basics Swimming',14).define(';Swimming;10h'))

    #s.resetDistances()
    #s.parseFile('Training{}.csv'.format(date.today().year))

    return s



config.colors = {'Bicycle': '#ffdddd', 'Running': '#ddffdd', 'K': '#aaffaa', 'Swimming': '#ddddff'}
#print(config.getSettingsStr())

s = PlanSimple('Season Simple').schedule(date.today()).updateValues({'Running': 6.0, 'Bicycle': 20.0, 'Swimming': 2.0})

# patch some days using a scheduled cycle
#c = Cycle('Pause Running').insert([1,3,5],Unit('10;Running;3:00:00')).schedule(date.today().year,7,2)
#print('info: ' + str(c), file=sys.stderr)
#s.insertByDate(c,True)

#s.insert(Period('Sickness',14).fix(date.today() + timedelta(days=60)).setColor('#ff0000'),1)
s.insert(Period('Sickness + Recovery').append([Period('Sickness',4).setColor('#ff0000'),Period('Recovery',10).define([';Running;3h'])]).fix(date.today() + timedelta(days=60)),1)

print(s.report())
#print(s.toTemplate())

#quit()


f = open('DraftPlanGantt.svg', encoding='utf-8', mode='w')
f.write(s.toSVGGanttChart())
f.close()

f = open('DraftPlan.svg', encoding='utf-8', mode='w')
f.write(s.toSVGDiagram())
f.close()

f = open('DraftPlan.mm', encoding='utf-8', mode='w')
f.write(s.toFreeMind())
f.close()

f = open('DraftPlan.ics', 'wb')
f.write(s.toVCalendar())
f.close()

f = open('DraftPlan.txt', encoding='utf-8', mode='w')
f.write(s.toString())
f.close()

f = open('DraftPlan.csv', encoding='utf-8', mode='w')
f.write(s.toCSV())
f.close()

f = open('DraftPlan.html', encoding='utf-8', mode='w')
f.write(s.toHtmlFile())
f.close()

