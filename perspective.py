#
#
#

import sys
import datetime

from training.period import Period

from training import config as config

config.bar_height = 16
config.colors = {'W': '#ff5555', 'R': '#ffdddd', 'L': '#ddffdd', 'K': '#aaffaa', 'S': '#ddddff'}

from templates import Draft
from templates import Triathlon
from templates import Season2021

def Perspective(strArg):

    p = Period(strArg)

    f = 1.0
    y = datetime.date.today().year
    for i in range(y,y+5):
        #p.append(Period(f'Season {i}').CalendarMonthPeriod(i))
        #p.append(Triathlon.Season(f'Season {i}').updateValues().schedule(i,3,4).scale(f))
        #p.append(Season2021.Season(f'Season {i}').updateValues().schedule(i,1,4).scale(f))
        p.append(Draft.Season(f'Season {i}').updateValues().schedule(i,1,4).scale(f))
        f = f * 1.2

    return p


p = Perspective('Starting ' + datetime.date.today().isoformat())
print(p.report())
p.writeFiles('output','perspective')
