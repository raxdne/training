#
# Data Management for Physical Training
#
# Copyright (C) 2021,2022,2023 by Alexander Tenbusch
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

def __fixIt__(listArg=[]):

    """ fix nesting """

    listResult = []

    if type(listArg) is list and len(listArg) == 1 and type(listArg[0]) is list:
        return __fixIt__(listArg[0])
    elif type(listArg[0]) is str:
        for e in listArg[1:]:
            if type(e) is list and len(e) == 1 and type(e[0]) is str:
                listResult.append(e[0])
            elif type(e) is list:
                listResult.append(__fixIt__(e))

        return [listArg[0],listResult]
    else:
        return listArg


def __appendTo__(intDepth=0,listArg=[],strArg=''):

    # search for last element where depth < intDepth => parent list

    l = listArg
    d = 0
    while d < intDepth and type(l[-1]) is list:
        l = l[-1]
        d += 1

    #print("{} {}".format(d, strArg))
    l.append([strArg])


#
#
#

class Description:

    """ abstract class to handle (nested) description list """

    def __init__(self,strArg=None):

        """  """
        
        self.color = None
        self.listDescription = []

        self.setDescription(strArg)


    def __str__(self):

        """ returns a string of nested self.listDescription """

        return str(self.__listDescriptionToString__())


    def setDescription(self,objArg=None):

        """  """

        if objArg == None or len(objArg) < 1:
            self.listDescription = []
        elif type(objArg) is str:
            self.listDescription.append([objArg])
        elif type(objArg) is list:
            self.listDescription = [objArg]
        else:
            self.listDescription = []


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


    def parseDescription(self,strArg):

        """  """

        """ https://stackoverflow.com/questions/45964731/how-to-parse-hierarchy-based-on-indents-with-python """

        indentation = []
        indentation.append(0)
        depth = 0
        r = []

        for line in strArg.splitlines():

            content = line.strip()
            indent = len(line) - len(content)

            if indent > indentation[-1]:
                depth += 1
                indentation.append(indent)

            elif indent < indentation[-1]:
                while indent < indentation[-1]:
                    depth -= 1
                    indentation.pop()

                if indent != indentation[-1]:
                    raise RuntimeError("Bad formatting")

            #print(f"{content} (depth: {depth})")
            __appendTo__(depth,r,content)

        self.appendDescription(__fixIt__(r))


    def setColor(self,strColor=None):

        """  """

        if strColor != None and len(strColor) > 0:
            self.color = strColor
        else:
            self.color = None

        return self


    def __listDescriptionToString__(self,listArg=None):

        """ returns a CSV string of nested self.listDescription """

        strResult = ''

        if listArg == None:
            strResult += self.__listDescriptionToString__(self.listDescription)
        elif type(listArg) is list and len(listArg) == 2 and type(listArg[0]) is str and type(listArg[1]) is list:
            strResult += ' {}'.format(listArg[0]) + self.__listDescriptionToString__(listArg[1])
        elif type(listArg) is list and len(listArg) > 0:
            for c in listArg:
                if type(c) is str:
                    strResult += ' ' + c
                elif type(c) is list:
                    strResult += self.__listDescriptionToString__(c)
                else:
                    print('fail: ',c, file=sys.stderr)

        return strResult


    def __listDescriptionToSVG__(self,listArg=None):

        """ returns a XML/SVG string of nested self.listDescription """

        strResult = self.__listDescriptionToString__().replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;")

        return strResult


    def __listDescriptionToHtml__(self,listArg=None):

        """ returns a HTML string of nested self.listDescription """

        #strResult = '<div>'
        strResult = ''

        if listArg == None:
            strResult += self.__listDescriptionToHtml__(self.listDescription)
        elif type(listArg) is list and len(listArg) == 2 and type(listArg[0]) is str and type(listArg[1]) is list:
            # list item + childs
            strResult += '<li>' + listArg[0] + '</li>\n<ul>' + self.__listDescriptionToHtml__(listArg[1]) + '</ul>\n'
        elif type(listArg) is list and len(listArg) > 0:
            # list items
            for c in listArg:
                if type(c) is str:
                    strResult += '<li>' + c.replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;") + '</li>\n'
                elif type(c) is list:
                    strResult += self.__listDescriptionToHtml__(c)
                else:
                    print('fail: ',c, file=sys.stderr)

        #strResult += '</div>'

        return strResult


    def __listDescriptionToFreemind__(self,listArg=None):

        """ returns a Freemind XML string of nested self.listDescription """

        strResult = ''

        if listArg == None:
            strResult += self.__listDescriptionToFreemind__(self.listDescription)
        elif type(listArg) is str and len(listArg) > 0:
            strResult += '<node TEXT="{}"/>\n'.format(listArg.replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;"))
        elif type(listArg) is list and len(listArg) == 2 and type(listArg[0]) is str and type(listArg[1]) is list:
            """ tupel (str . list) """

            strResult += '<node FOLDED="{}" TEXT="{}">\n'.format('true',listArg[0]) + ''

            for c in listArg[1:]:
                strResult += self.__listDescriptionToFreemind__(c)

            strResult += '</node>\n'

        elif type(listArg) is list:
            """ a list, but single element only """
            for c in listArg:
                strResult += self.__listDescriptionToFreemind__(c)
        else:
            print('fail: ',listArg, file=sys.stderr)

        return strResult


    def __listDescriptionToXML__(self):

        """  """

        return self.__listDescriptionToString__().replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;")


