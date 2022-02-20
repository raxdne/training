#
# Data Management for Physical Training
#
# Copyright (C) 2021,2022 by Alexander Tenbusch
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

#
#
#

class Description:

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
                    strResult += '<li>' + c + '</li>\n'
                elif type(c) is list:
                    strResult += self.__listDescriptionToHtml__(c)
                else:
                    print('fail: ',c, file=sys.stderr)

        #strResult += '</div>'

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


if __name__ == "__main__":

    print('Module Test:\n')
    
    d = Description(['ABC','DEF'])

    d.appendDescription(['WWW',['YYY','ZZZ']])

    print(d.__listDescriptionToString__())

    print(d.__listDescriptionToHtml__())

    print(d.__listDescriptionToXML__())

    print(d.hasDescription())

