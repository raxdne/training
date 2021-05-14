#
# Object Model for a Bicycle
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

import re
import copy
import math

#
# https://en.wikipedia.org/wiki/Bicycle
#

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
            

#
#
#

class part(title,description):

    """  """
    
    def __init__(self,strArg=None):
        
        """ constructor """
        
        self.listChilds = []
        self.setTitleStr(strArg)
        self.listDescription = []
        #self.setDescription(strArg)


    def mount(self,objPart=None):

        """  """

        if objPart == None:
            pass
        elif isinstance(self, bicycle) and isinstance(objPart, frame):
            self.listChilds.append(objPart)
        elif isinstance(self, frame) and (isinstance(objPart, wheel) or isinstance(objPart, crankset)):
            self.listChilds.append(objPart)
        elif isinstance(self, wheel) and (isinstance(objPart, rear_sprockets) or isinstance(objPart, tyre)):
            self.listChilds.append(objPart)
        elif isinstance(self, crankset) and (isinstance(objPart, chainrings) or isinstance(objPart, pedal)):
            self.listChilds.append(objPart)
        else:
            print("Not mountable: '{}' at '{}'".format(type(objPart),type(self)))
        return self


    def getPartsListStr(self):

        """  """

        strResult = ''
            
        m = re.match(r"<class '__main__\.([a-zA-Z_]+)'>",str(type(self)))
        if m != None:
            strResult += " " + m.group(1)

        if self.hasTitle():
            strResult += ' "' + self.getTitleStr() + '"'
        strResult += "\n"
        
        if len(self.listChilds) > 0:
            for c in self.listChilds:
                strResult += c.getPartsListStr()
                
        return strResult    

    
    def getRelations(self):

        """  """

        strResult = ''
            
        m = re.match(r"<class '__main__\.([a-zA-Z_]+)'>",str(type(self)))
        if m != None:
            strType = m.group(1)

            if self.hasTitle():
                strResult += strType + ' [label="' + self.getTitleStr() + '"]\n'
        
            if len(self.listChilds) > 0:
                for c in self.listChilds:
                    mc = re.match(r"<class '__main__\.([a-zA-Z_]+)'>",str(type(c)))
                    if mc != None:
                        strResult += mc.group(1) + ' -> ' + strType + '\n'
                        strResult += c.getRelations()
                
        return strResult    

    
class frame(part):

    """  """

    def set(self,chain_stay=None):
        
        """  """

        self.chain_stay = chain_stay
    

class pedal(part):

    """  """
    

class tyre(part):

    """  """
    

class wheel(part):

    """  """
    
    def set(self,floatArg=None):
        
        """  """

        self.circumference = floatArg


class rear_sprockets(part):

    """  """
    
    def set(self,listArg=None):
        
        """  """

        if len(listArg) > 0 and len(listArg) < 13:
            self.w = sorted(listArg,reverse=True)
            

class chainrings(part):

    """  """
    
    def set(self,listArg=None):
        
        """  """

        if len(listArg) > 0 and len(listArg) < 4:
            self.w = sorted(listArg)
            

class crankset(part):

    """  """

    def set(self, crank_length=170.0, bcd=130.0):
        
        """  """

        self.length = crank_length
        self.bcd = bcd

    
class chain(part):

    """  """
    

class bicycle(part):

    """  """
    
    def getChainLength(self):
        
        """  """

        for f in self.listChilds:
            if isinstance(f, frame):
                for c in f.listChilds:
                    if isinstance(c, wheel):
                        for cc in c.listChilds:
                            if isinstance(cc, rear_sprockets):
                                #print(rear_sprockets)
                                rs = cc
                    elif isinstance(c, crankset):
                        for cc in c.listChilds:
                            if isinstance(cc, chainrings):
                                #print(chainrings)
                                cr = cc

        r_max = 0
        for r in cr.w:
             if r > r_max:
                 r_max = r
                 
        s_max = 0
        for s in rs.w:
            if s > s_max:
                 s_max = s

        n = math.ceil(0.157 * f.chain_stay * 1000 + r_max / 2 + s_max / 2 + 2)
        if n % 2 != 0:
            n += 1

        print(r_max,'/',s_max,' ',f.chain_stay,'mm', '   ',n,' chain links')

        
    def getGearRatios(self,listArg=None):
        
        """  """

        for f in self.listChilds:
            if isinstance(f, frame):
                for c in f.listChilds:
                    if isinstance(c, wheel):
                        w = c
                        for cc in c.listChilds:
                            if isinstance(cc, rear_sprockets):
                                rs = cc
                    elif isinstance(c, crankset):
                        for cc in c.listChilds:
                            if isinstance(cc, chainrings):
                                cr = cc
                                
        for r in cr.w:
            if cr.w.index(r) == 0:
                # smallest chain ring
                for s in rs.w[0:len(rs.w) - 2]:
                    print('{}/{} = {:.02f}  {:.02f}m'.format(r,s,r/s,r/s*w.circumference))
            elif cr.w.index(r) == len(cr.w) - 1:
                # largest chain ring
                f = 100.0
                for s in rs.w[2:]:
                    print('{}/{} = {:.02f}  {:.02f}m {:.0f} km/h at {:.0f} 1/min'.format(r,s,r/s,r/s*w.circumference,f*60*r/s*w.circumference/1000, f))
            else:
                # medium chain ring
                for s in rs.w[1:len(rs.w) - 1]:
                    print('{}/{} = {:.02f}  {:.02f}m'.format(r,s,r/s,r/s*w.circumference))


    def getGraph(self):
        
        """  """

        strResult = 'digraph "Bicycle" {\n'
        strResult += self.getRelations()
        strResult += '}\n'

        return strResult

