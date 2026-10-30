#
#
#

import sys

from datetime import date, datetime, timedelta

from training.note import Note
from training.pause import Pause
from training.unit import Unit
from training.exerciseset import ExerciseSet
from training.combination import Combination
from training.cycle import Cycle
from training.period import Period
from training.phase import Phase
from training.bunch import Bunch
from training import utils

import training.config as config


def RegenerationGeneral():

    r = Bunch('General Regeneration',7).append([(2,Unit(';Bicycle;1h')),Unit(';Running;30min')])

    return r.set(color='#eeeeee')


def BasicsGeneral():

    p = Bunch('General Basics',4*7).append([(5,Unit(';Bicycle;1h')),(5,Unit(';Running;30min'))])
    p.appendDescription(['General physical Basics',['Core','Flexibility','']])

    return p


def BasicsBicycle():
    
    p = Bunch('Basics Endurance Bicycle',6*7).append((10,Unit(';Bicycle;2h')))
    p.appendDescription('Weight, Metabolism, Nutrition')
    
    return p


def BuildupBicycleSpeed():

    p = Bunch('Buildup Bicycle Speed',3*7).append((10,Unit(';Bicycle;2h')))
    p.appendDescription('Sprint Final speed')
    
    return p


def HighlightBicycle1():
    c = Cycle('Highlight Bicycle Distance').set(color='#ffffaa')
    
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
    
    p = Bunch('Specific Basics Running',5*7).append([(4,Unit(';Bicycle;1h')),(16,Unit(';Running;30min'))])
    p.appendDescription('Change of Focus')

    return p


def BuildupRunningSpeed():

    p = Bunch('Buildup Running Speed',4*7).append([(4,Unit(';Bicycle;1h')),(16,Unit(';Running;30min'))])
    
    return p


def HighlightRunning1():

    c = Cycle('Highlight Running Distance').set(color='#ffffaa')

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
    s.append(Bunch('Basics Swimming',14).append((20,Unit(';Swimming;30min'))))

    #s.resetDistances()
    #s.parseFile('Training{}.csv'.format(date.today().year))

    return s


if __name__ == '__main__':

    s = Season('Season Simple').schedule(datetime.today().year,3,1)
    s.updateValues({'Running': 6.0, 'Bicycle': 20.0, 'Swimming': 2.0})
    print(s.report())
    s.setTextOnly(False)
    s.writeFiles('Output','Draft')

