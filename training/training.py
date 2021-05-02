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

import math

import copy

import re

from datetime import (
    timedelta,
    date,
    datetime,
    time
)

#from suntime import Sun

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
                    print('fail: ',c)

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
                if type(c) is str:
                    strResult += '<node BACKGROUND_COLOR="{}" TEXT="{}"/>\n'.format('#ffffaa',c)
                elif type(c) is list:
                    strResult += self.__listDescriptionToXML__(c)
                else:
                    print('fail: ',c)

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
        
        # TODO: make colorcoding configurable
        self.color = {'W': '#ff5555', 'R': '#ffdddd', 'L': '#ddffdd', 'K': '#aaaaff', 'S': '#ddddff'}
        # TODO: implement a self.unitDist = (km|mi)
        self.dist = None
        self.type = None
        self.time = None
        self.date = None
        self.clock = None
        self.setDescription()

        
    def setTypeStr(self,strArg):

        """  """
        
        if strArg == None or strArg == '':
            pass
        else:
            self.type = strArg.replace(' ','')
        return True
        

    def setDistStr(self,strArg):

        """  """
        
        if strArg == None or strArg == '':
            pass
        else:
            self.dist = float(strArg)
            if self.dist < 0.001:
                self.dist = None

        return True


    def setTimeStr(self,strArg):

        """  """
        
        if strArg == None or strArg == '':
            self.time = time()
        else:
            entry = strArg.split(':')
            if len(entry) == 2:
                self.time = time(minute=int(entry[0]), second=int(entry[1]))
            elif len(entry) == 3:
                self.time = time(hour=int(entry[0]), minute=int(entry[1]), second=int(entry[2]))
            else:
                self.time = time()
                
        return True


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
                    #print("date: ",m.group(0))
                    self.date = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                else:
                    m = re.match(r"([0-2][0-9]:[0-5]{2})",strArg)
                    if m != None:
                        #print("time: ",m.group(1))
                        self.clock = time.fromisoformat("{}:00".format(m.group(1)))
                    else:
                        print('ignoring: ',strArg)

        return True


    def scale(self,floatScale,patternType=None):

        """  """

        if patternType == None or re.match(patternType,self.type):
            
            if self.dist == None or self.dist < 0.01:
                pass
            else:
                self.dist *= floatScale

            if self.time == None:
                pass
            else:
                minutes = (self.time.hour * 60 + self.time.minute)
                minutes *= floatScale
                self.time = time(hour=int(minutes / 60), minute=int(minutes % 60))


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
            if self.setDistStr(objArg[1]) and self.setTypeStr(objArg[2]) and self.setTimeStr(objArg[3]):
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
        if self.dist == None or self.dist < 0.01 or self.time == None:
            pass
        else:
            s = float(self.time.hour * 3600 + self.time.minute * 60 + self.time.second)
            if s < 1:
                pass
            else:
                spk = s / self.dist
                strResult += '{0}:{1:02} min/km '.format(int(spk // 60), int(spk % 60))
                strResult += '{:.0f} km/h '.format(self.dist / (s / 3600))
            
        return strResult

    
    def getSunStr(self):

        """  """

        latitude = 47.8
        longitude = 9.6

        sun = Sun(latitude, longitude)

        abd_sr = sun.get_local_sunrise_time(self.date)
        abd_ss = sun.get_local_sunset_time(self.date)

        return '{} -- {}'.format(abd_sr.strftime('%H:%M'), abd_ss.strftime('%H:%M'))


    def toString(self):

        """  """

        if self.type == None and self.dist == None and self.date == None:
            strResult = 'EMPTY'
        elif self.type == None:
            strResult = '{date}'.format(date=self.date.isoformat())
        elif self.dist == None or self.dist < 0.01:
            strResult = '{date} {type} {time}'.format(date=self.date.isoformat(), type=self.type, time=self.time.isoformat())
        elif self.date == None:
            strResult = '{date} {dist:5.1f} {type} {time}'.format(date='', dist=self.dist, type=self.type, time=self.time.isoformat())
        else:
            strResult = '{date} {dist:5.1f} {type} {time}'.format(date=self.date.isoformat(), dist=self.dist, type=self.type, time=self.time.isoformat())

        #strResult += self.__listDescriptionToPlain__()
        
        return strResult


    def toCSV(self):

        """  """
        
        if self.type == None:
            strResult = '{date};;;'.format(date=self.date.isoformat())
        elif self.dist == None or self.dist < 0.01:
            strResult = '{date};;{type};{time}'.format(date=self.date.isoformat(), type=self.type, time=self.time.isoformat())
        else:
            strResult = '{date};{dist:.1f};{type};{time}'.format(date=self.date.isoformat(), dist=self.dist, type=self.type, time=self.time.isoformat())

        strResult += ';' + self.__listDescriptionToPlain__()
                
        return strResult


    def toXML(self):

        """  """
        
        strResult = '<node'

        strResult += ' TEXT="' + self.toString() + '"'

        if self.type != None and len(self.type) > 0 and self.type[0] in self.color:
            strResult += ' BACKGROUND_COLOR="{}"'.format(self.color[self.type[0]])
        strResult += '>'
        
        if self.dist != None and self.dist > 0.01:
            strResult += '<node TEXT="' + self.getSpeedStr() + '"/>'
            #strResult += '<node TEXT="' + self.getSunStr() + '"/>'
            
        strResult += self.__listDescriptionToXML__()
                
        strResult += '</node>\n'

        return strResult


    def toiCalString(self):

        """  """

        dateNow = datetime.now()

        strResult = 'BEGIN:VEVENT\n'

        if self.type == None:
            strResult += "SUMMARY:{description}\n".format(description = self.__listDescriptionToPlain__())
        elif self.dist == None or self.dist < 0.01:
            strResult += "SUMMARY:{type} {time}\n".format(type=self.type, time=self.time.isoformat())
        else:
            strResult += "SUMMARY:{dist:.0f} {type} {time}\n".format(dist=self.dist, type=self.type, time=self.time.isoformat())

        if self.hasDescription():
            strResult += 'DESCRIPTION:{}\n'.format(self.__listDescriptionToPlain__())

        if self.clock == None or self.time == None:
            strResult += "DTSTART;{y:04}{m:02}{d:02}\nDTEND;{y:04}{m:02}{d:02}\n".format(y=self.date.year, m=self.date.month, d=self.date.day)
        else:
            t = datetime(self.date.year, self.date.month, self.date.day, self.clock.hour, self.clock.minute)
            strResult += "DTSTART;{y:04}{m:02}{d:02}T{h:02}{min:02}{s:02}\n".format(y=t.year, m=t.month, d=t.day, h=t.hour, min=t.minute, s=0)
            t += timedelta(hours = self.time.hour, minutes = self.time.minute)
            strResult +=   "DTEND;{y:04}{m:02}{d:02}T{h:02}{min:02}{s:02}\n".format(y=t.year, m=t.month, d=t.day, h=t.hour, min=t.minute, s=0)

        strResult += "DTSTAMP;{y:04}{m:02}{d:02}T{h:02}{min:02}{s:02}\n".format(y=dateNow.year, m=dateNow.month, d=dateNow.day, h=dateNow.hour, min=dateNow.minute, s=dateNow.second)

        strResult += 'END:VEVENT\n'
        
        return strResult



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

        self.lengthType = 10
        self.periodInt = intArg
        
        self.child = []
        for i in range(0,int(intArg)):
            self.child.append([])

        self.dateBegin = date.today()
        self.dateEnd = date.today()

        
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
        
        if objUnit != None and objUnit.date != None and self.dateBegin <= objUnit.date and objUnit.date <= self.dateEnd:
            objResult = objUnit.dup()
            delta = objResult.date - self.dateBegin
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

        return intResult


    def getTypeOfUnits(self,arrArg=None):

        """  """
        
        if arrArg == None:
            arrArg = []
            
        for v in self.child:
            for u in v:
                if u.type != None and len(u.type) > 0:
                    k = u.type[0:self.lengthType]
                    if k in arrArg:
                        pass
                    else:
                        arrArg.append(k)

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
                if u.dist == None or u.dist < 0.01 or u.type == None or len(u.type) < 1:
                    pass
                else:
                    k = u.type[0:self.lengthType]
                    arrArg[u.date.month - 1][k] += u.dist


    def report(self, arrArg=None):

        """  """
        
        if arrArg == None:
            arrArg = {}
            
        strResult = ''

        for v in self.child:
            for u in v:
                if u.type != None and len(u.type) > 0:
                    k = u.type[0:self.lengthType]
                    if k in arrArg:
                        if u.dist != None and u.dist > 0.01:
                            arrArg[k][0] += u.dist
                        arrArg[k][1] += 1
                        arrArg[k][2] += u.time.hour * 3600 + u.time.minute * 60 + u.time.second
                    else:
                        arrArg[k] = []
                        if u.dist != None and u.dist > 0.01:
                            arrArg[k].append(u.dist)
                        else:
                            arrArg[k].append(None)

                        arrArg[k].append(1)
                        arrArg[k].append(u.time.hour * 3600 + u.time.minute * 60 + u.time.second)
                    
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

    
    def toXML(self):

        """  """
        
        strResult = '<node'
        
        if self.getNumberOfUnits() < 1:
            strResult += ' BACKGROUND_COLOR="{}"'.format('#ffaaaa')
        else:
            strResult += ' FOLDED="{}"'.format('true')
            
        strResult += ' TEXT="' + self.getTitleStr() + '&#xa;(' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '">\n'
        
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
        
        for c in self.child:
            c.insertByDate(objUnit)


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

        for k in sorted(arrArg.keys()):
            if arrArg[k][0] == None or arrArg[k][0] < 0.01:
                strResult += "{:4} x {:3} {:5}    {:5.0f} h\n".format(arrArg[k][1], k, ' ', round(arrArg[k][2] / 3600, 1))
            else:
                strResult += "{:4} x {:3} {:5.0f} km {:5.0f} h\n".format(arrArg[k][1], k, arrArg[k][0], round(arrArg[k][2] / 3600, 1))        
        n = self.getNumberOfUnits()
        if n > 0:
            p = self.getPeriod()
            strResult += "{:4} Units in {} Days = {:.02f} Units/Week\n".format(n, p, n/p * 7.0)
            
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


    def parseFile(self,filename):

        """  """
        
        print("* ",filename)
        with open(filename) as f:
            content = f.read().splitlines()
        f.close()

        t = unit()
        for l in content:
            if l == None or l == '':
                pass
            elif t.parse(l):
                self.insertByDate(t)
            else:
                print('error: ' + l)

            
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

        
    def toVCalendar(self):

        """  """
        
        strResult = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//{title}//  //\n".format(title=self.getTitleStr())
        for c in self.child:
            strResult += c.toiCalString()
        strResult += "END:VCALENDAR"
        
        return strResult


#
#
#

def CalendarPeriod(intYear):

    """ returns a plain calendar year period """
    
    s = period(str(intYear))

    try:
        datetime.date(intYear, 2, 29)
        s.append(cycle('All',366))
    except ValueError:
        s.append(cycle('All',365))

    s.schedule(intYear,1,1)

    return s
  
        
def CalendarMonthPeriod(intYear):

    """ returns a calendar year containing month periods """
    
    s = period(str(intYear))

    for m in range(1,13):
        if m > 11:
            d = date(intYear+1,1,1) - date(intYear,m,1)
        else:
            d = date(intYear,m+1,1) - date(intYear,m,1)

        p = period(str(intYear) + '.' + str(m))
        p.append(cycle(str(m), d.days))
        s.append(p)
        
    s.schedule(intYear,1,1)

    return s
  
        
