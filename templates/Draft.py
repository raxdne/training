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


def Season(strArg):

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


if __name__ == '__main__':

    s = Season('Season Simple').schedule(datetime.date.today().year,3,1)
    s.updateValues({'Running': 6.0, 'Bicycle': 20.0, 'Swimming': 2.0})
    print(s.report())
    s.writeFiles('output','SeasonSimple')


