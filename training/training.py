#
# Data Management for Physical Training
#
# Copyright (C) 2021 by Alexander Tenbusch
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

import sys

import math

import copy

import re

from datetime import (
    date,
    datetime,
    time,
    timedelta,
    timezone
)

#from suntime import Sun

from icalendar import Calendar, Event

#
# Module Variables
#

diagram_scale_dist = 6

diagram_bar_height = 8

diagram_offset = 175

diagram_width = diagram_offset + 6 * 25 * diagram_scale_dist

font_family = 'Arial'

font_size = 8

# default colors in diagram
colors = {'W': '#ff5555', 'R': '#ffdddd', 'L': '#ddffdd', 'K': '#aaaaff', 'S': '#ddddff'}

# maximum for length of type string
max_length_type = 10

# distance unit 'mi' or 'km'
unit_distance = 'km'

#
twilight = 1800
sun = None

#
#
#
def getSettingsStr():

    """ returns a Python string containing all module settings """

    strResult = '# Diagram\n'
    strResult += 'diagram_scale_dist = {}\n'.format(diagram_scale_dist)
    strResult += 'diagram_bar_height = {}\n'.format(diagram_bar_height)
    strResult += 'diagram_offset = {}\n'.format(diagram_offset)
    strResult += 'diagram_width = {}\n'.format(diagram_width)
    strResult += 'font_family = {}\n'.format(font_family)
    strResult += 'font_size = {}\n'.format(font_size)

    strResult += 'colors = {}\n'.format(colors)
    strResult += 'max_length_type = {}\n'.format(max_length_type)
    strResult += 'unit_distance = \'{}\'\n'.format(unit_distance)

    return strResult

#
#
#

class title:

    """ abstract class to handle title """

    def __init__(self,strArg=None):

        """ constructor """

        self.setTitleStr(strArg)


    def setTitleStr(self,strArg):

        """  """

        self.strTitle = strArg


    def hasTitle(self):

        """  """

        return self.strTitle != None and len(self.strTitle) > 0


    def getTitleStr(self):

        """  """

        return self.strTitle



#
#
#

class description:

    """ abstract class to handle description list """

    def __init__(self,strArg=None):

        """ constructor """

        self.listDescription = []
        self.setDescription(strArg)


    def setDescription(self,objArg=None):

        """  """

        if objArg == None or len(objArg) < 1:
            self.listDescription = []
        elif type(objArg) is str:
            self.listDescription.append([objArg])
        elif type(objArg) is list:
            self.listDescription = [objArg]


    def hasDescription(self):

        """  """

        return self.listDescription != None and len(self.listDescription) > 0


    def appendDescription(self,objArg):

        """  """

        if objArg == None or len(objArg) < 1:
            pass
        elif len(self.listDescription) < 1:
            self.setDescription(objArg)
        elif type(objArg) is str:
            self.listDescription.append([objArg])
        elif type(objArg) is list:
            self.listDescription.append(objArg)


    def __listDescriptionToPlain__(self,listArg=None):

        """ returns a CSV string of nested self.listDescription """

        strResult = ''

        if listArg == None:
            strResult += self.__listDescriptionToPlain__(self.listDescription)
        elif type(listArg) is list and len(listArg) == 2 and type(listArg[0]) is str and type(listArg[1]) is list:
            strResult += ' {}'.format(listArg[0]) + self.__listDescriptionToPlain__(listArg[1])
        elif type(listArg) is list and len(listArg) > 0:
            for c in listArg:
                if type(c) is str:
                    strResult += c + ' '
                elif type(c) is list:
                    strResult += self.__listDescriptionToPlain__(c)
                else:
                    print('fail: ',c, file=sys.stderr)

        return strResult


    def __listDescriptionToXML__(self,listArg=None):

        """ returns a Freemind XML string of nested self.listDescription """

        strResult = ''

        if listArg == None:
            strResult += self.__listDescriptionToXML__(self.listDescription)
        elif type(listArg) is list and len(listArg) == 2 and type(listArg[0]) is str and type(listArg[1]) is list:
            strResult += '<node TEXT="{}">\n'.format(listArg[0]) + self.__listDescriptionToXML__(listArg[1]) + '</node>\n'
        elif type(listArg) is list and len(listArg) > 0:
            for c in listArg:
                if len(c) < 1:
                    pass
                elif type(c) is str and len(c) > 0:
                    strResult += '<node BACKGROUND_COLOR="{}" TEXT="{}"/>\n'.format('#ffffaa',c)
                elif type(c) is list:
                    strResult += self.__listDescriptionToXML__(c)
                else:
                    print('fail: ',c, file=sys.stderr)

        return strResult


#
#
#

class unit(description):

    """ class for training units """

    def __init__(self,strArg=None):

        """ constructor """

        if strArg == None:
            self.reset()
        else:
            self.parse(strArg)


    def reset(self):

        """  """

        self.dist = None
        self.type = None
        self.duration = None
        self.date = None
        self.clock = None
        self.setDescription()


    def setTypeStr(self,strArg):

        """  """

        if strArg == None or strArg == '':
            pass
        else:
            self.type = strArg.replace(' ','')[0:max_length_type]
        return True


    def setDistStr(self,strArg):

        """  """

        if strArg == None or strArg == '':
            self.dist = None
        else:
            self.dist = float(strArg)
            if self.dist < 0.001:
                self.dist = None

        return True


    def setDurationStr(self,strArg):

        """  """

        if strArg == None or strArg == '':
            self.duration = timedelta(0)
        else:
            entry = strArg.split(':')
            if len(entry) == 1:
                # nothing to split
                entry = strArg.split('min')
                if len(entry) == 2:
                    self.duration = timedelta(minutes=int(entry[0]))
                else:
                    entry = strArg.split('h')
                    if len(entry) == 2:
                        self.duration = timedelta(hours=int(entry[0]))
                    else:
                        self.duration = timedelta(0)
            elif len(entry) == 2:
                self.duration = timedelta(minutes=int(entry[0]), seconds=int(entry[1]))
            elif len(entry) == 3:
                self.duration = timedelta(hours=int(entry[0]), minutes=int(entry[1]), seconds=int(entry[2]))
            else:
                self.duration = timedelta(0)

        return True


    def getDurationStr(self):

        """  """

        if self.duration == None:
            return "0:00:00"
        else:
            seconds = self.duration.total_seconds()
            return time(hour = int(seconds // 3600), minute = int((seconds % 3600) // 60), second = int(seconds % 60)).strftime("%H:%M:%S")


    def setDate(self,objArg):

        """  """

        self.date = objArg


    def setDateStr(self,strArg):

        """  """

        if strArg == None or strArg == '':
            pass
        else:
            m = re.match(r"\s*([0-9]{4}-*[0-9]{2}-*[0-9]{2})[\sT]+([0-2][0-9]:[0-5]{2})\s*",strArg)
            if m != None:
                #print("date + time: ",m.group(1), " ",m.group(2))
                self.setDateStr(m.group(1))
                self.setDateStr(m.group(2))
            else:
                m = re.match(r"([0-9]{4})-*([0-9]{2})-*([0-9]{2})",strArg)
                if m != None:
                    #print("date: ",m.group(0), file=sys.stderr)
                    self.date = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                else:
                    m = re.match(r"([0-2][0-9]:[0-5]{2})",strArg)
                    if m != None:
                        #print("time: ",m.group(1), file=sys.stderr)
                        self.clock = time.fromisoformat("{}:00".format(m.group(1)))
                    else:
                        print('ignoring: ',strArg, file=sys.stderr)

        return True


    def scale(self,floatScale,patternType=None):

        """  """

        if floatScale > 0.1 and (patternType == None or re.match(patternType,self.type)):

            if self.dist != None:
                if self.dist < 15.0:
                    self.dist *= floatScale
                else:
                    # round distance to 5.0
                    self.dist = round(self.dist * floatScale / 5.0) * 5.0

            if self.duration != None:
                s = self.duration.total_seconds()
                if s < 900.0:
                    self.duration *= floatScale
                else:
                    # round duration to 5:00 min
                    self.duration = timedelta(seconds=(round(s * floatScale / 300.0) * 300.0))


    def dup(self):

        """  """

        return copy.deepcopy(self)


    def parse(self,objArg):

        """  """

        if objArg == None or len(objArg) < 1:
            return False
        elif type(objArg) is str:
            entry = objArg.split(';')
            # TODO: test elements of entry
            if len(entry) == 3:
                entry.insert(0,'')
            return self.parse(entry)
        elif type(objArg) is list and len(objArg) > 3:
            self.reset()
            if self.setDistStr(objArg[1]) and self.setTypeStr(objArg[2]) and self.setDurationStr(objArg[3]):
                self.setDateStr(objArg[0])
                self.appendDescription(objArg[4:])
                return True
            else:
                return False
        else:
            return False


    def getSpeedStr(self):

        """  """

        strResult = ''
        if self.dist == None or self.duration == None:
            pass
        else:
            s = float(self.duration.total_seconds())
            if s < 1:
                pass
            else:
                spk = s / self.dist
                strResult += '{}:{:02} min/{} '.format(int(spk // 60), int(spk % 60), unit_distance)
                strResult += '{:.0f} {}/h '.format(self.dist / (s / 3600), unit_distance)

        return strResult


    def toString(self):

        """  """

        if self.type == None and self.dist == None and self.date == None:
            strResult = 'EMPTY'
        elif self.type == None:
            strResult = '{date} {duration}'.format(date=self.date.isoformat(), duration=self.getDurationStr())
        elif self.dist == None:
            strResult = '{date} {type} {duration}'.format(date=self.date.isoformat(), type=self.type, duration=self.getDurationStr())
        elif self.date == None:
            strResult = '{date} {dist:5.1f} {type} {duration}'.format(date='', dist=self.dist, type=self.type, duration=self.getDurationStr())
        else:
            strResult = '{date} {dist:5.1f} {type} {duration}'.format(date=self.date.isoformat(), dist=self.dist, type=self.type, duration=self.getDurationStr())

        #strResult += self.__listDescriptionToPlain__()

        return strResult


    def toCSV(self):

        """  """

        if self.type == None:
            strResult = '{date};;;'.format(date=self.date.isoformat())
        elif self.dist == None:
            strResult = '{date};;{type};{duration}'.format(date=self.date.isoformat(), type=self.type, duration=self.getDurationStr())
        else:
            strResult = '{date};{dist:.1f};{type};{duration}'.format(date=self.date.isoformat(), dist=self.dist, type=self.type, duration=self.getDurationStr())

        strResult += ';' + self.__listDescriptionToPlain__()

        return strResult


    def toSVG(self,x,y):

        """  """

        strResult = ''

        if self.duration == None or self.duration.total_seconds() < 60:
            strResult += '<text x="{}" y="{}">{}<title>{}</title></text>\n'.format(x + diagram_bar_height / 2, y + diagram_bar_height, self.__listDescriptionToPlain__(), self.toString())
        else:
            strResult += '<rect '

            if self.type == None or len(self.type) < 1:
                strResult += ' fill="{}"'.format('#cccccc')
            elif self.type[0] in colors:
                strResult += ' fill="{}"'.format(colors[self.type[0]])

            if self.dist == None or True:
                # "about 25 distance units per hour"
                bar_width = self.duration.total_seconds() / 3600 * 25 * diagram_scale_dist
            else:
                bar_width = self.dist * diagram_scale_dist

            strResult += ' height="{}px" stroke="black" stroke-width=".5" width="{:.0f}px" x="{}" y="{}"'.format(diagram_bar_height, bar_width, x, y)
            strResult += '>'

            strResult += '<title>{}: {}</title>'.format(self.toString(), self.__listDescriptionToPlain__())

            strResult += '</rect>\n'

        return strResult


    def toXML(self):

        """  """

        strResult = '<node'

        strResult += ' TEXT="' + self.toString() + '"'

        if self.type != None and len(self.type) > 0 and self.type[0] in colors:
            strResult += ' BACKGROUND_COLOR="{}"'.format(colors[self.type[0]])
        strResult += '>'

        if self.dist != None:
            strResult += '<node TEXT="' + self.getSpeedStr() + '"/>'

        strResult += self.__listDescriptionToXML__()

        strResult += '</node>\n'

        return strResult


    def toiCalString(self):

        """  """

        dateNow = datetime.now()

        strResult = 'BEGIN:VEVENT\n'

        if self.type == None:
            strResult += "SUMMARY:{description}\n".format(description = self.__listDescriptionToPlain__())
        else:
            strResult += "SUMMARY:{type} {time}\n".format(type=self.type, time=self.getDurationStr())
            if self.hasDescription():
                strResult += 'DESCRIPTION:{}\n'.format(self.__listDescriptionToPlain__())

        if self.clock == None or self.duration == None:
            strResult += self.date.strftime("DTSTART;%Y%m%d\nDTEND;%Y%m%d\n")
        else:
            t0 = datetime.combine(self.date, self.clock).astimezone(None)
            t1 = t0 + self.duration

            if sun != None:
                # fix 't' according to sunrise/sunset
                t_earliest = sun.get_local_sunrise_time(self.date) + timedelta(seconds=twilight)
                t_latest = sun.get_local_sunset_time(self.date) - timedelta(seconds=twilight)

                if t_earliest > t0:
                    # shift start time after twilight
                    t0 = t_earliest
                    # adjust to 15min steps
                    t0 -= timedelta(minutes=(t0.minute % 15))
                    t1 = t0 + self.duration
                elif t_latest < t1:
                    # shift end time before twilight
                    t0 = t_latest - self.duration
                    t0 -= timedelta(minutes=(t0.minute % 15))
                    t1 = t0 + self.duration

            #print(self.date,' ',self.clock,' ',self.type,' ',t0,' ',t_latest,file=sys.stderr)

            strResult += t0.strftime("DTSTART;%Y%m%dT%H%M%S\n")
            strResult += t1.strftime("DTEND;%Y%m%dT%H%M%S\n")

        strResult += dateNow.strftime("DTSTAMP;%Y%m%dT%H%M%S\n")

        strResult += 'END:VEVENT\n'

        return strResult


    def to_ical(self,cal):

        """  """

        event = Event()

        if self.type == None:
            event.add('summary', self.__listDescriptionToPlain__())
        else:
            event.add('summary', "{} {}".format(self.type, self.getDurationStr()))
            if self.hasDescription():
                event.add('description', self.__listDescriptionToPlain__())

        if self.clock == None or self.duration == None:
            event.add('dtstart', self.date)
            event.add('dtend', self.date + timedelta(days=1))
        else:
            t0 = datetime.combine(self.date, self.clock).astimezone(None)
            t1 = t0 + self.duration

            if sun != None:
                # fix 't' according to sunrise/sunset
                t_earliest = sun.get_local_sunrise_time(self.date) + timedelta(seconds=twilight)
                t_latest = sun.get_local_sunset_time(self.date) - timedelta(seconds=twilight)

                if t_earliest > t0:
                    # shift start time after twilight
                    t0 = t_earliest
                    # adjust to 15min steps
                    t0 -= timedelta(minutes=(t0.minute % 15))
                    t1 = t0 + self.duration
                elif t_latest < t1:
                    # shift end time before twilight
                    t0 = t_latest - self.duration
                    t0 -= timedelta(minutes=(t0.minute % 15))
                    t1 = t0 + self.duration

            #print(self.date,' ',self.clock,' ',self.type,' ',t0,' ',t_latest,file=sys.stderr)

            event.add('dtstart', t0)
            event.add('dtend', t1)

        # TODO: add reminder
        event.add('dtstamp', datetime.now().astimezone(None))
        cal.add_component(event)



#
#
#

class cycle(title,description):

    def __init__(self,strArg=None,intArg=7):

        """ constructor """

        self.reset(strArg,intArg)


    def reset(self,strArg=None,intArg=7):

        """  """

        self.setTitleStr(strArg)
        self.setDescription()

        self.periodInt = intArg

        self.child = []
        for i in range(0,int(intArg)):
            self.child.append([])

        self.dateBegin = date.today()
        self.dateEnd = date.today()


    def resetDistances(self):

        """  """

        for v in self.child:
            for u in v:
                u.setDistStr(None)


    def resetUnits(self):

        """  """

        for v in self.child:
            del v[0:]


    def getLength(self):

        """  """

        return len(self.child)


    def insert(self,intIndex,objUnit):

        """  """

        objResult = None

        if objUnit != None:
            objResult = objUnit.dup()
            self.child[intIndex].append(objResult)

        return objResult


    def insertByDate(self,objUnit):

        """  """

        objResult = None

        if objUnit != None and objUnit.date != None:
            delta = objUnit.date - self.dateBegin
            if delta.days > -1 and objUnit.date <= self.dateEnd:
                objResult = objUnit.dup()
                self.child[delta.days].append(objResult)

        return objResult


    def insertDescriptionStr(self,intIndex,strArg):

        """  """

        if strArg == None or strArg == '':
            pass
        elif len(self.child) > intIndex and len(self.child[intIndex]) > 0:
            self.child[intIndex][len(self.child[intIndex]) - 1].appendDescription(strArg)


    def getPeriod(self):

        """  """

        return len(self.child)


    def getNumberOfUnits(self):

        """  """

        intResult = 0
        for v in self.child:
            for u in v:
                if u.type != None and len(u.type) > 0:
                    intResult += 1
                elif u.duration != None and u.duration.total_seconds() > 59:
                    intResult += 1

        return intResult


    def getTypeOfUnits(self,arrArg=None):

        """  """

        if arrArg == None:
            arrArg = []

        for v in self.child:
            for u in v:
                if u.type != None and len(u.type) > 0:
                    if u.type in arrArg:
                        pass
                    else:
                        arrArg.append(u.type)

        return arrArg


    def scale(self,floatScale,patternType=None):

        """  """

        for v in self.child:
            for u in v:
                u.scale(floatScale,patternType)


    def schedule(self, intYear, intMonth, intDay):

        """  """

        d = date(intYear, intMonth, intDay)

        for v in self.child:
            o = self.child.index(v)
            for u in v:
                u.setDate(d + timedelta(days=o))

        self.dateBegin = date(intYear, intMonth, intDay)
        self.dateEnd = self.dateBegin + timedelta(days=(self.getPeriod() - 1))


    def stat(self, arrArg):

        """  """

        for v in self.child:
            for u in v:
                if u.dist == None or u.type == None or len(u.type) < 1:
                    pass
                else:
                    arrArg[u.date.month - 1][u.type] += u.dist


    def report(self, arrArg=None):

        """  """

        if arrArg == None:
            arrArg = {}

        strResult = ''

        for v in self.child:
            for u in v:
                if u.type != None and len(u.type) > 0:
                    if u.type in arrArg:
                        if u.dist != None:
                            if arrArg[u.type][0] == None:
                                arrArg[u.type][0] = u.dist
                            else:
                                arrArg[u.type][0] += u.dist
                        arrArg[u.type][1] += 1
                        arrArg[u.type][2] += u.duration.total_seconds()
                    else:
                        arrArg[u.type] = []
                        if u.dist != None:
                            arrArg[u.type].append(u.dist)
                        else:
                            arrArg[u.type].append(None)

                        arrArg[u.type].append(1)
                        arrArg[u.type].append(u.duration.total_seconds())

        sum_h = 0.0
        for k in sorted(arrArg.keys()):
            if arrArg[k][0] == None or arrArg[k][0] < 0.01:
                strResult += "{:4} x {:3} {:5}    {:5.0f} h\n".format(arrArg[k][1], k, ' ', round(arrArg[k][2] / 3600, 1))
            else:
                strResult += "{:4} x {:3} {:5.0f} {} {:5.0f} h\n".format(arrArg[k][1], k, arrArg[k][0], unit_distance, round(arrArg[k][2] / 3600, 1))        
            sum_h += arrArg[k][2]

        sum_h /= 3600.0
        n = self.getNumberOfUnits()
        if n > 0:
            p = self.getPeriod()
            strResult += "{:4} h     in {} Days = {:4.01f} h/Week\n".format(round(sum_h), p, sum_h/p * 7.0)

        return strResult


    def dup(self):

        """  """

        return copy.deepcopy(self)


    def toString(self):

        """  """

        strResult = '\n** ' + self.getTitleStr() + ' (' + str(self.getPeriod()) + ', ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n\n'
        for v in self.child:
            for u in v:
                strResult += u.toString() + '\n'
        return strResult


    def toCSV(self):

        """  """

        strResult = '\n* ' + self.getTitleStr() + ' (' + str(self.getPeriod()) + ', ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n'
        for v in self.child:
            for u in v:
                strResult += u.toCSV() + '\n'
        return strResult


    def toSVG(self,x,y):

        """  """

        strResult = '<g>'

        strResult += '<line stroke="black" stroke-width=".5" stroke-dasharray="2,10" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(0,y,x+diagram_width,y)

        strResult += '<text x="{}" y="{}" style="vertical-align:top" text-anchor="right"><tspan x="10" dy="1.5em">{}</tspan><tspan x="10" dy="1.5em">{}</tspan></text>\n'.format(0,y,self.getTitleStr(), '(' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')')

        if len(self.child) < 1:
            pass
        else:
            y += diagram_bar_height / 2
            t = date.today()
            d = self.dateBegin
            for v in self.child:
                strResult += '<line stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(x,y,x,y+diagram_bar_height)

                if d.month == t.month and d.day == t.day:
                    strResult += '<rect fill="{}" x="{}" y="{}" height="{}px" width="{}px"/>\n'.format('#ffaaaa',x,y-1,diagram_bar_height+2,diagram_width - diagram_offset)
                elif d.isoweekday() == 6 or d.isoweekday() == 7:
                    strResult += '<rect fill="{}" x="{}" y="{}" height="{}px" width="{}px"/>\n'.format('#eeeeee',x,y-1,diagram_bar_height+2,diagram_width - diagram_offset)
                d += timedelta(days=1)

                x_i = x

                for u in v:
                    # all units first
                    if u.type != None:
                        strResult += u.toSVG(x_i,y)
                        x_i += u.duration.total_seconds() / 3600 * 25 * diagram_scale_dist

                for u in v:
                    # all remarks after
                    if u.type == None:
                        strResult += u.toSVG(x_i,y)
                        x_i += len(u.toString()) * font_size

                y += diagram_bar_height * 2

        strResult += '</g>'

        return strResult


    def toXML(self):

        """  """

        strResult = '<node'

        if self.getNumberOfUnits() < 1:
            strResult += ' BACKGROUND_COLOR="{}"'.format('#ffaaaa')
        else:
            strResult += ' FOLDED="{}"'.format('true')

        strResult += ' TEXT="' + self.getTitleStr() + '&#xa;(' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')&#xa;' + self.report().replace('\n','&#xa;') + '">\n'
        strResult += '<font BOLD="false" NAME="Monospaced" SIZE="12"/>'

        strResult += self.__listDescriptionToXML__()

        for v in self.child:
            for u in v:
                strResult += u.toXML()
        strResult += '</node>\n'

        return strResult


    def toiCalString(self):

        """  """

        e = self.dateEnd + timedelta(days=1)

        if self.getNumberOfUnits() < 1:
            strResult = "BEGIN:VEVENT\nSUMMARY:Period {title}\nDTSTART;{y:04}{m:02}{d:02}\nDTEND;{ye:04}{me:02}{de:02}\nDTSTAMP;{y:04}{m:02}{d:02}\nEND:VEVENT\n".format(title=self.getTitleStr(), y=self.dateBegin.year, m=self.dateBegin.month, d=self.dateBegin.day, ye=e.year, me=e.month, de=e.day)
        else:
            strResult = ''
            for v in self.child:
                for u in v:
                    strResult += u.toiCalString()

        return strResult


    def to_ical(self,cal):

        """  """

        event = Event()
        event.add('summary', 'Cycle: {}'.format(self.getTitleStr()))
        event.add('dtstart', self.dateBegin)
        event.add('dtend', self.dateEnd + timedelta(days=1))
        event.add('dtstamp', datetime.now().astimezone(None))
        cal.add_component(event)

        for v in self.child:
            for u in v:
                u.to_ical(cal)


#
#
#

class period(title,description):

    def __init__(self,strArg=None,intArg=None):

        """ constructor """

        self.reset(strArg,intArg)


    def reset(self,strArg=None,intArg=None):

        """  """

        self.setTitleStr(strArg)
        self.setDescription()

        self.setPeriod(intArg)

        self.child = []
        self.dateBegin = date.today()
        self.dateEnd = date.today()


    def resetDistances(self):

        """  """

        for c in self.child:
            c.resetDistances()


    def resetUnits(self):

        """  """

        for c in self.child:
            c.resetUnits()


    def appendChildDescription(self,objArg):

        """  """

        if len(self.child) > 0:
            self.child[len(self.child) - 1].appendDescription(objArg)


    def getNumberOfUnits(self):

        """  """

        intResult = 0
        for c in self.child:
            intResult += c.getNumberOfUnits()

        return intResult


    def getTypeOfUnits(self,arrArg=None):

        """  """

        if arrArg == None:
            arrArg = []
        for c in self.child:
            c.getTypeOfUnits(arrArg)

        return arrArg


    def append(self,objChild):

        """  """

        c = objChild.dup()
        self.child.append(c)


    def insertByDate(self,objUnit):

        """  """

        objResult = None

        if objUnit != None and objUnit.date != None:
            if len(self.child) < 1:
                # there is no child cycle yet
                delta = objUnit.date - self.dateBegin
                if delta.days > -1 and objUnit.date <= self.dateEnd:
                    l = self.dateEnd - self.dateBegin
                    c = cycle(self.getTitleStr(), l.days + 1)
                    c.schedule(self.dateBegin.year,self.dateBegin.month,self.dateBegin.day)
                    objResult = c.insertByDate(objUnit)
                    if objResult != None:
                        self.append(c)
            else:        
                for c in self.child:
                    objResult = c.insertByDate(objUnit)
                    if objResult != None:
                        break

        return objResult


    def setPeriod(self, intArg):

        """  """

        self.periodInt = intArg


    def getPeriod(self):

        """  """

        l = 0
        for c in self.child:
            l += c.getPeriod()

        if self.periodInt == None or l > self.periodInt:
            self.setPeriod(l)

        return self.periodInt


    def scale(self,floatScale,patternType=None):

        """  """

        for c in self.child:
            c.scale(floatScale,patternType)


    def schedule(self, intYear, intMonth, intDay):

        """  """

        d = date(intYear, intMonth, intDay)

        for c in self.child:
            c.schedule(d.year, d.month, d.day)
            d += timedelta(days=c.getPeriod())

        self.dateBegin = date(intYear, intMonth, intDay)
        self.dateEnd = self.dateBegin + timedelta(days=(self.getPeriod() - 1))


    def report(self, arrArg=None):

        """  """

        if arrArg == None:
            arrArg = {}
        strResult = ''

        for c in self.child:
            c.report(arrArg)

        sum_h = 0.0
        for k in sorted(arrArg.keys()):
            if arrArg[k][0] == None or arrArg[k][0] < 0.01:
                strResult += "{:4} x {:3} {:5}    {:5.0f} h\n".format(arrArg[k][1], k, ' ', round(arrArg[k][2] / 3600, 1))
            else:
                strResult += "{:4} x {:3} {:5.0f} {} {:5.0f} h\n".format(arrArg[k][1], k, arrArg[k][0], unit_distance, round(arrArg[k][2] / 3600, 1))        
            sum_h += arrArg[k][2]

        sum_h /= 3600.0
        n = self.getNumberOfUnits()
        if n > 0:
            p = self.getPeriod()
            #strResult += "{:4} Units in {} Days = {:4.01f} Units/Week\n".format(n, p, n/p * 7.0)
            strResult += "{:4} h     in {} Days = {:4.01f} h/Week\n".format(round(sum_h), p, sum_h/p * 7.0)

        return strResult


    def stat(self, arrArg=None):

        """  """

        t = sorted(self.getTypeOfUnits())
        if arrArg == None:
            arrArg = []
            for m in range(12):
                a = {}
                for u in t:
                    a[u] = 0.0
                arrArg.append(a)

        strResult = self.getTitleStr() + '\n'

        for c in self.child:
            c.stat(arrArg)

        for u in t:
            strResult += "\t{}".format(u)

        for m in range(12):
            strResult += "\n{}".format(m+1)
            for u in arrArg[m]:
                strResult += "\t{:.0f}".format(arrArg[m][u])

        return strResult


    def parseFile(self,listFilename):

        """  """

        if type(listFilename) == str:
            listFilename = [listFilename]

        a = []
        d0 = None
        d1 = None
        t = unit()

        for filename in listFilename:
            print("* ",filename, file=sys.stderr)
            with open(filename) as f:
                content = f.read().splitlines()
            f.close()

            for l in content:
                if l == None or l == '':
                    pass
                elif t.parse(l) and t.date != None:
                    if d0 == None or t.date < d0:
                        d0 = t.date
                    if d1 == None or t.date > d1:
                        d1 = t.date
                    a.append(t)
                    t = unit()
                else:
                    print('error: ' + l, file=sys.stderr)

        print('Report {} .. {}'.format(d0.isoformat(),d1.isoformat()), file=sys.stderr)

        delta = d1 - d0

        if len(self.child) > 0:
            # there is a child list already
            pass
        elif delta.days < 365:
            for y in range(d0.year,d1.year+1):
                self.append(CalendarWeekPeriod(y))
        elif delta.days < 3 * 365:
            for y in range(d0.year,d1.year+1):
                self.append(CalendarMonthPeriod(y))
        else:
            for y in range(d0.year,d1.year+1):
                self.append(CalendarYearPeriod(y))

        for t in a:
            #print(t.toString())
            self.insertByDate(t)


    def dup(self):

        """  """

        return copy.deepcopy(self)


    def toString(self):

        """  """

        strResult = '\n* ' + self.getTitleStr() + ' (' + str(self.getPeriod()) + ' ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n\n'
        for c in self.child:
            strResult += c.toString() + '\n'
        return strResult


    def toCSV(self):

        """  """

        strResult = '\n* ' + self.getTitleStr() + ' (' + str(self.getPeriod()) + ' ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n'
        for c in self.child:
            strResult += c.toCSV() + '\n'
        return strResult


    def toXML(self):

        """  """

        strResult = '<node'
        if self.getNumberOfUnits() < 1:
           strResult += ' BACKGROUND_COLOR="{}"'.format('#ffaaaa')
        else:
            strResult += ' FOLDED="{}"'.format('false')

        strResult += ' TEXT="' + self.getTitleStr() + '&#xa; (' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')&#xa;' + self.report().replace('\n','&#xa;') + '">\n'
        strResult += '<font BOLD="true" NAME="Monospaced" SIZE="12"/>'

        strResult += self.__listDescriptionToXML__()

        for c in self.child:
            strResult += c.toXML()
        strResult += '</node>\n'
        return strResult


    def toFreeMind(self):

        """  """

        strResult = '<map>\n'
        strResult += self.toXML()
        strResult += '</map>\n'
        return strResult


    def toSVG(self,x= diagram_offset ,y=20):

        """  """

        strResult = '<g>'

        if len(self.child) < 1:
            strResult += '<text x="{}" y="{}" style="vertical-align:top"><tspan x="10" dy="1.5em">{}</tspan><tspan x="10" dy="1.5em">{}</tspan></text>\n'.format(0,y,self.getTitleStr(), '(' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')')
            strResult += '<line stroke="black" stroke-width=".5" stroke-dasharray="2,10" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(0,y,x+diagram_width,y)
            for d in range(0,self.getPeriod()):
                strResult += '<line stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(x,y,x,y+diagram_bar_height)
                y += diagram_bar_height * 2
        else:
            for c in self.child:
                #strResult += '<line stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(x,y,x+400,y)
                #strResult += '<text x="{}" y="{}">{}</text>\n'.format(x+400,y,c.getTitleStr())
                strResult += c.toSVG(x,y)
                y += c.getPeriod() * diagram_bar_height * 2

        strResult += '</g>'

        return strResult


    def toSVGDiagram(self):

        """  """

        diagram_height = self.getPeriod() * (diagram_bar_height * 2) + 100
        strResult = '<svg baseProfile="full" height="{}px" version="1.1" width="{}px" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink">'.format(diagram_height, diagram_width)

        strResult += '<style type="text/css">svg { font-family: ' + font_family + '; font-size: ' + str(font_size) + 'pt; }</style>'

        #strResult += '<g transform="rotate(90)">'
        #'<text x="210" y="110">Period 2.2021</text>

        for i in [3600/4,3600/2,3600,2*3600,3*3600,4*3600,5*3600,6*3600]:
            w = i / 3600 * 25 * diagram_scale_dist
            strResult += '<line stroke="black" stroke-width=".5" x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format( diagram_offset + w, 20, diagram_offset + w, diagram_height)

        strResult += self.toSVG()
        #strResult += '</g>'
        strResult += '</svg>\n'
        return strResult


    def toiCalString(self):

        """  """

        e = self.dateEnd + timedelta(days=1)

        if len(self.child) < 1:
            strResult = "BEGIN:VEVENT\nSUMMARY:Period {title}\nDTSTART;{y:04}{m:02}{d:02}\nDTEND;{ye:04}{me:02}{de:02}\nDTSTAMP;{y:04}{m:02}{d:02}\nEND:VEVENT\n".format(title=self.getTitleStr(), y=self.dateBegin.year, m=self.dateBegin.month, d=self.dateBegin.day, ye=e.year, me=e.month, de=e.day)
        else:
            strResult = ''
            for c in self.child:
                strResult += c.toiCalString()

        return strResult


    def to_ical(self,cal):

        """  """

        event = Event()
        event.add('summary', 'Period: {}'.format(self.getTitleStr()))
        event.add('dtstart', self.dateBegin)
        event.add('dtend', self.dateEnd + timedelta(days=1))
        event.add('dtstamp', datetime.now().astimezone(None))
        cal.add_component(event)

        for c in self.child:
            c.to_ical(cal)


    def toVCalendar(self):

        """  """

        try:
            cal = Calendar()
            cal.add('prodid', '-//{title}//  //'.format(title=self.getTitleStr()))
            cal.add('version', '2.0')
            self.to_ical(cal)
            return cal.to_ical()
        except NameError:
            # TODO: remove all toiCalString() legacy code
            strResult = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//{title}//  //\n".format(title=self.getTitleStr())
            for c in self.child:
                strResult += c.toiCalString()
            strResult += "END:VCALENDAR"
            return strResult

#
#
#

def CalendarYearPeriod(intYear):

    """ returns a plain calendar year period """

    try:
        date(intYear, 2, 29)
        s = cycle(str(intYear),366)
    except ValueError:
        s = cycle(str(intYear),365)

    s.schedule(intYear,1,1)

    return s


def CalendarWeekPeriod(intYear):

    """ returns a calendar year containing week periods """

    s = period(str(intYear))

    for w in range(1,54):
        u = 'CW' + str(w) + '/' + str(intYear)
        c = cycle(u, 7)
        s.append(c)

    d = date(intYear,1,1)
    if d.isoweekday() > 4:
        # skip to next monday
        d += timedelta(days=(8 - d.isoweekday())) 
    else:
        # skip to previous monday
        d -= timedelta(days=(d.isoweekday() - 1))

    s.schedule(d.year,d.month,d.day)

    return s


def CalendarMonthPeriod(intYear):

    """ returns a calendar year containing month periods """

    s = period(str(intYear))

    for m in range(1,13):
        if m > 11:
            d = date(intYear+1,1,1) - date(intYear,m,1)
        else:
            d = date(intYear,m+1,1) - date(intYear,m,1)

        c = cycle(str(intYear) + '.' + str(m),d.days)
        s.append(c)

    s.schedule(intYear,1,1)

    return s
