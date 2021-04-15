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

from datetime import (
    timedelta,
    date,
    datetime,
    time
)

#
#
#

class unit:
    
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
        self.time = None
        self.arrComment = []

        
    def setTypeStr(self,strArg):
        if strArg == None or strArg == '':
            self.type = ''
        else:
            self.type = strArg.replace(' ','')
        return True
        

    def appendCommentStr(self,strArg):
        if strArg == None or strArg == '':
            self.arrComment = []
        else:
            self.arrComment.append(strArg)


    def setDistStr(self,strArg):
        if strArg == None or strArg == '':
            pass
        else:
            self.dist = float(strArg)
            if self.dist < 0.001:
                self.dist = None

        return True


    def setTimeStr(self,strArg):
        
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


    def setDateTime(self,objArg):
        
        self.DateTime = objArg
        

    def setDateStr(self,strArg):
        #print(strArg[0] + strArg[1] + strArg[2] + strArg[3] + '-' + strArg[4] + strArg[5] + '-' + strArg[6] + strArg[7])
        if strArg == None or strArg == '':
            self.setDateTime(date.today())
        elif len(strArg) == 8:
            return self.setDateStr(strArg[0] + strArg[1] + strArg[2] + strArg[3] + '-' + strArg[4] + strArg[5] + '-' + strArg[6] + strArg[7])
        else:
            entry = strArg.split('-')
            if len(entry) == 3:
                self.setDateTime(date(int(entry[0]),int(entry[1]),int(entry[2])))
            else:
                self.setDateTime(date.today())
        return True


    def scale(self,floatScale):

        if self.dist == None or self.dist < 0.01:
            pass
        else:
            self.dist *= floatScale
            
        minutes = (self.time.hour * 60 + self.time.minute)
        minutes *= floatScale
        self.time = time(hour=int(minutes / 60), minute=int(minutes % 60))


    def dup(self):
        return copy.deepcopy(self)


    def parse(self,strArg):
        """  """

        self.reset()
        entry = strArg.split(';')
        if len(entry) == 3:
             return self.parse(';' + strArg)
        elif len(entry) > 3 and self.setDistStr(entry[1]) and self.setTypeStr(entry[2]) and self.setTimeStr(entry[3]):
            self.setDateStr(entry[0])

            self.arrComment = []
            for i in range(4,len(entry)):
                self.appendCommentStr(entry[i])

            return True
        else:
            return False
        

    def getSpeedStr(self):

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
                kph = self.dist / (s / 3600)
                strResult += '{:.1f} km/h '.format(kph)
            
        return strResult
    

    def toString(self):
        return "{date} {dist:5.0f} {type} {time} {comment}\n".format(date=self.DateTime.isoformat(), dist=self.dist, type=self.type, time=self.time.isoformat(), comment='')


    def toCSV(self):
        return "{date};{dist:.0f};{type};{time};{comment}\n".format(date=self.DateTime.isoformat(), dist=self.dist, type=self.type, time=self.time.isoformat(), comment='')


    def toXML(self):

        # TODO: make colorcoding configurable
        c = {'W': '#ff5555', 'R': '#ffdddd', 'L': '#ddffdd', 'K': '#aaaaff', 'S': '#ddddff'}

        if self.dist == None or self.dist < 0.01:
            strResult = ' TEXT="{date} {type} {time}"'.format(date=self.DateTime.isoformat(), type=self.type, time=self.time.isoformat())
            strC = ''
        else:
            strResult = ' TEXT="{date} {dist:.1f} {type} {time}"'.format(date=self.DateTime.isoformat(), dist=self.dist, type=self.type, time=self.time.isoformat())
            strC = '<node TEXT="' + self.getSpeedStr() + '"/>'

        if len(self.type) > 0 and self.type[0] in c:
            strResult += ' BACKGROUND_COLOR="' + c[self.type[0]] + '"'

        if len(self.arrComment) > 0:
            for i in self.arrComment:
                strC += '<node TEXT="' + i + '"/>'
            
        return '<node' + strResult + '>' + strC + '</node>\n'


    def toSQL(self):

        if self.dist == None or self.dist < 0.01:
            return "insert ({date};{dist:.0f};{type};{time};{comment})\n".format(date=self.DateTime.isoformat(), dist=0.0, type=self.type, time=self.time.isoformat(), comment='')
        else:
            return "insert ({date};{dist:.0f};{type};{time};{comment})\n".format(date=self.DateTime.isoformat(), dist=self.dist, type=self.type, time=self.time.isoformat(), comment='')


    def toiCalString(self):
        
        if self.dist == None or self.dist < 0.01:
            return "BEGIN:VEVENT\nSUMMARY:{type} {time} {comment}\nDTSTART;VALUE=DATE:{y:04}{m:02}{d:02}\nDTEND;VALUE=DATE:{y:04}{m:02}{d:02}\nDTSTAMP;VALUE=DATE:{y:04}{m:02}{d:02}\nEND:VEVENT\n".format(y=self.DateTime.year, m=self.DateTime.month, d=self.DateTime.day, type=self.type, time=self.time.isoformat(), comment='')
        else:
            return "BEGIN:VEVENT\nSUMMARY:{dist:.0f} {type} {time} {comment}\nDTSTART;VALUE=DATE:{y:04}{m:02}{d:02}\nDTEND;VALUE=DATE:{y:04}{m:02}{d:02}\nDTSTAMP;VALUE=DATE:{y:04}{m:02}{d:02}\nEND:VEVENT\n".format(y=self.DateTime.year, m=self.DateTime.month, d=self.DateTime.day, dist=self.dist, type=self.type, time=self.time.isoformat(), comment='')


#
#
#

class cycle:

    def __init__(self,strArg=None,intArg=7):
        """ constructor """

        self.reset(strArg,intArg)

        
    def reset(self,strArg=None,intArg=7):

        self.strTitle = strArg
        self.arrDescription = []

        self.lengthType = 1
        self.periodInt = intArg
        
        self.child = []
        for i in range(0,int(intArg)):
            self.child.append([])

        self.dateBegin = date.today()
        self.dateEnd = date.today()

        
    def resetUnits(self):

        for v in self.child:
            del v[0:]

        
    def appendDescriptionStr(self,strArg):
        if strArg == None or strArg == '':
            self.arrDescription = []
        else:
            self.arrDescription.append(strArg)
        

    def setTitleStr(self,strArg):
        self.strTitle = strArg
        

    def getLength(self):
        return len(self.child)
    

    def insert(self,intIndex,objUnit):

        self.child[intIndex].append(objUnit.dup())

        
    def insertByDate(self,objUnit):

        if self.dateBegin <= objUnit.DateTime and objUnit.DateTime <= self.dateEnd:
            delta = objUnit.DateTime - self.dateBegin
            self.child[delta.days].append(objUnit.dup())


    def insertDescriptionStr(self,intIndex,strArg):
        
        if strArg == None or strArg == '':
            None
        elif len(self.child) > intIndex and len(self.child[intIndex]) > 0:
            self.child[intIndex][len(self.child[intIndex]) - 1].appendCommentStr(strArg)
        

    def getPeriod(self):
        return len(self.child)
            

    def getNumberOfUnits(self):
        intResult = 0
        for v in self.child:
            intResult += len(v)

        return intResult


    def getTypeOfUnits(self,arrArg=None):

        if arrArg == None:
            arrArg = []
            
        for v in self.child:
            for u in v:
                k = u.type[0:self.lengthType]
                if len(k) < 1:
                    pass
                elif k in arrArg:
                    None
                else:
                    arrArg.append(k)

        return arrArg

    
    def scale(self,floatScale):
        for v in self.child:
            for u in v:
                u.scale(floatScale)


    def schedule(self, intYear, intMonth, intDay):

        d = date(intYear, intMonth, intDay)
        
        for v in self.child:
            o = self.child.index(v)
            for u in v:
                u.setDateTime(d + timedelta(days=o))
                    
        self.dateBegin = date(intYear, intMonth, intDay)
        self.dateEnd = self.dateBegin + timedelta(days=(self.getPeriod() - 1))


    def stat(self, arrArg):

        for v in self.child:
            for u in v:
                k = u.type[0:self.lengthType]
                arrArg[u.DateTime.month - 1][k] += u.dist


    def report(self, arrArg=None):

        if arrArg == None:
            arrArg = {}
        strResult = ''

        for v in self.child:
            for u in v:
                k = u.type[0:self.lengthType]
                if len(k) < 1:
                    pass
                elif k in arrArg:
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
        return copy.deepcopy(self)


    def toString(self):
        strResult = '\n' + self.strTitle + ' (' + str(self.getPeriod()) + ', ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n'
        for v in self.child:
            for u in v:
                strResult += u.toString()
        return strResult


    def toCSV(self):
        strResult = '\n*' + self.strTitle + ' (' + str(self.getPeriod()) + ', ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n'
        for v in self.child:
            for u in v:
                strResult += u.toCSV()
        return strResult

    
    def toXML(self):
        strResult = '<node FOLDED="true" TEXT="' + self.strTitle + '&#xa;(' + str(self.getPeriod()) + ' ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '">\n'
        for d in self.arrDescription:
            strResult += '<node BACKGROUND_COLOR="#ffffaa" TEXT="' + d + '"/>\n'
        for v in self.child:
            for u in v:
                strResult += u.toXML()
        strResult += '</node>\n'
        return strResult

    
    def toiCalString(self):

        strResult = ''
        for v in self.child:
            for u in v:
                strResult += u.toiCalString()
                
        return strResult

        

#
#
#

class period:

    def __init__(self,strArg=None,intArg=None):
        """ constructor """

        self.reset(strArg,intArg)

        
    def reset(self,strArg=None,intArg=None):
        
        self.strTitle = strArg
        self.arrDescription = []
        self.setPeriod(intArg)

        self.child = []
        self.dateBegin = date.today()
        self.dateEnd = date.today()

        
    def resetUnits(self):

        for c in self.child:
            c.resetUnits()

            
    def appendDescriptionStr(self,strArg):
        if strArg == None or strArg == '':
            self.arrDescription = []
        else:
            self.arrDescription.append(strArg)
        

    def appendChildDescriptionStr(self,strArg):
        if strArg == None or strArg == '':
            None
        elif len(self.child) > 0:
            self.child[len(self.child) - 1].appendDescriptionStr(strArg)
        

    def setTitleStr(self,strArg):
        self.strTitle = strArg
        

    def getNumberOfUnits(self):
        intResult = 0
        for c in self.child:
            intResult += c.getNumberOfUnits()

        return intResult


    def getTypeOfUnits(self,arrArg=None):

        if arrArg == None:
            arrArg = []
        for c in self.child:
            c.getTypeOfUnits(arrArg)

        return arrArg

    
    def append(self,objChild):

        c = objChild.dup()
        self.child.append(c)


    def insertByDate(self,objUnit):
        for c in self.child:
            c.insertByDate(objUnit)


    def setPeriod(self, intArg):

        self.periodInt = intArg
            

    def getPeriod(self):

        l = 0
        for c in self.child:
            l += c.getPeriod()
            
        if self.periodInt == None or l > self.periodInt:
            self.setPeriod(l)
            
        return self.periodInt
            

    def scale(self,floatScale):
        for c in self.child:
            c.scale(floatScale)


    def schedule(self, intYear, intMonth, intDay):

        d = date(intYear, intMonth, intDay)
        
        for c in self.child:
            c.schedule(d.year, d.month, d.day)
            d += timedelta(days=c.getPeriod())
                    
        self.dateBegin = date(intYear, intMonth, intDay)
        self.dateEnd = self.dateBegin + timedelta(days=(self.getPeriod() - 1))


    def report(self, arrArg=None):

        if arrArg == None:
            arrArg = {}
        strResult = self.strTitle + '\n'

        for c in self.child:
            #strResult += c.report()
            c.report(arrArg)

        n = self.getNumberOfUnits()
        if n > 0:
            p = self.getPeriod()
            strResult += str(n) + ' Units in ' + str(p) + ' Days = ' + '{:.02f}'.format(n/p * 7.0) + ' Units/Week' + '\n'
            
        for k in sorted(arrArg.keys()):
            if arrArg[k][0] == None or arrArg[k][0] < 0.01:
                strResult += "{:3} x {:3} {:5}    {:5} h\n".format(arrArg[k][1], k, ' ', int(arrArg[k][2] / 3600))
            else:
                strResult += "{:3} x {:3} {:5.0f} km {:5} h\n".format(arrArg[k][1], k, arrArg[k][0], int(arrArg[k][2] / 3600))        

        return strResult


    def stat(self, arrArg=None):

        t = self.getTypeOfUnits()
        if arrArg == None:
            arrArg = []
            for m in range(12):
                a = {}
                for u in t:
                    a[u] = 0.0
                arrArg.append(a)
                
        strResult = self.strTitle + '\n'

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

        print("* ",filename)
        with open(filename) as f:
            content = f.read().splitlines()
        f.close()

        t = unit()
        for l in content:
            if l == None or l == '':
                print('skip: ' + l)
            elif t.parse(l):
                self.insertByDate(t)

            
    def dup(self):
        return copy.deepcopy(self)


    def toString(self):
        strResult = '\n' + self.strTitle + ' (' + str(self.getPeriod()) + ' ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n'
        for c in self.child:
            strResult += c.toString() + '\n'
        return strResult


    def toCSV(self):
        strResult = '\n*' + self.strTitle + ' (' + str(self.getPeriod()) + ' ' + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + ')' + '\n'
        for c in self.child:
            strResult += c.toCSV()
        return strResult

    
    def toXML(self):
        strResult = '<node TEXT="' + self.report().replace('\n','&#xa;') + self.dateBegin.isoformat() + ' .. ' + self.dateEnd.isoformat() + '">\n'
        strResult += '<font BOLD="true" NAME="Monospaced" SIZE="12"/>'
        for d in self.arrDescription:
            strResult += '<node BACKGROUND_COLOR="#ffffaa" TEXT="' + d + '"/>\n'
        for c in self.child:
            strResult += c.toXML()
        strResult += '</node>\n'
        return strResult

    
    def toFreeMind(self):
        strResult = '<map>\n'
        strResult += self.toXML()
        strResult += '</map>\n'
        return strResult

    
    def toiCalString(self):

        e = self.dateEnd + timedelta(days=1)
        
        strResult = ''
        # strResult += "BEGIN:VEVENT\nSUMMARY:Period {title}\nDTSTART;VALUE=DATE:{y:04}{m:02}{d:02}\nDTEND;VALUE=DATE:{ye:04}{me:02}{de:02}\nDTSTAMP;VALUE=DATE:{y:04}{m:02}{d:02}\nEND:VEVENT\n".format(title=self.strTitle, y=self.dateBegin.year, m=self.dateBegin.month, d=self.dateBegin.day, ye=e.year, me=e.month, de=e.day)

        for c in self.child:
            strResult += c.toiCalString()
                
        return strResult

        
    def toVCalendar(self):
        
        strResult = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//{title}//  //\n".format(title=self.strTitle)
        for c in self.child:
            strResult += c.toiCalString()
        strResult += "END:VCALENDAR"
        return strResult


#
#
#

def CalendarPeriod(intYear):

    ''' returns a plain calendar year period '''
    
    s = period(str(intYear))

    try:
        datetime.date(intYear, 2, 29)
        s.append(cycle('All',366))
    except ValueError:
        s.append(cycle('All',365))

    s.schedule(intYear,1,1)

    return s
  
        
def CalendarMonthPeriod(intYear):

    ''' returns a calendar year containing month periods '''
    
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
  
        
