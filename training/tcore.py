#
# Data Management for Physical Training
#
# Copyright (C) 2021,2022,2023,2026 by Alexander Tenbusch
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

import re
import copy
from abc import ABC, abstractmethod
from typing import final

# https://uibakery.io/regex-library/url-regex-python
url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"

re_garmin = re.compile('^garmin:([0-9]+)')
prefix_garmin = 'https://connect.garmin.com/app/activity/'


class TCore(ABC):

    """ abstract class for all common core methods """

    def __init__(self,t=''):

        """  """

        self.title = t
        self._descr = []


    def __imul__(self,f):
        
        return self.scale(f)


    @abstractmethod
    def scale(self,f,p=None):

        """  """

        pass


    @final
    def dup(self):

        """  """

        return copy.deepcopy(self)


    def toString(self):

        """  """

        return str(self)


    def __repr__(self):

        return f'{self.__class__.__name__}({self.title!r},{self._descr!r})'


    @property
    def description(self):

        """  """

        return self._descr


    @description.setter
    def description(self, o=None):

        """  """

        if o is None or not o:
            self._descr = []
        elif type(o) is str:
            self._descr.append(o)
        elif type(o) is list:
            self._descr.extend(o)


    def hasDescription(self):

        """  """

        return (hasattr(self,'_descr') and self._descr is not None and len(self._descr) > 0)


    def setDescription(self,o=None):

        """ wrapper for legacy code only """

        self.description = o

        return self


    def appendDescription(self,o):

        """ wrapper for legacy code only """

        if o is None or not o:
            pass
        elif not self._descr:
            self.description = o
        elif type(o) is str:
            self._descr.append(o)
        elif type(o) is list:
            self._descr.extend(o)

        return self


    def parseDescription(self,s):

        """  """

        """ https://stackoverflow.com/questions/45964731/how-to-parse-hierarchy-based-on-indents-with-python """

        indentation = []
        indentation.append(0)
        depth = 0
        r = []

        for line in s.splitlines():

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
            _appendTo(depth,r,content)

        self.appendDescription(_fixIt(r))


    def getDescriptionString(self,listArg=None):

        """ returns a string of nested self._descr """

        strResult = ''

        if listArg is None:
            strResult += self.getDescriptionString(self._descr)
        elif type(listArg) is list and len(listArg) == 2 and type(listArg[0]) is str and type(listArg[1]) is list:
            strResult += ' {}'.format(listArg[0]) + self.getDescriptionString(listArg[1])
        elif type(listArg) is list and listArg:
            for c in listArg:
                if type(c) is str:
                    strResult += ' ' + c
                elif type(c) is list:
                    strResult += self.getDescriptionString(c)

        return strResult


    def getDescriptionSVG(self,listArg=None):

        """ returns a XML/SVG string of nested self.description """

        strResult = self.getDescriptionString().replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;")

        return strResult


    def getDescriptionHTML(self,listArg=None):

        """ returns a HTML string of nested self.description """

        strResult = ''

        if listArg is None:
            f = _flatten(self.description)
            if len(f) == 1:
                # only one item
                if re.match(re_garmin, f[0]):
                    strResult += f' <a target="_blank" href="{prefix_garmin}{re.match(re_garmin, f[0]).group(1)}">Garmin</a>'
                elif re.match(url_pattern, f[0]):
                    strResult += ' <a target="_blank" href="{url}">{url}</a>'.format(url=f[0].replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;"))
                else:
                    strResult += ' <span>' + f[0].replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;") + '</span>'
            elif len(f) > 1:
                strResult += '<ul>' + self.getDescriptionHTML(self.description) + '</ul>'
        elif type(listArg) is list and len(listArg) == 2 and type(listArg[0]) is str and type(listArg[1]) is list:
            # list item + childs
            strResult += '<li>'
            if re.match(re_garmin, listArg[0]):
                strResult += f'<a target="_blank" href="{prefix_garmin}{re.match(re_garmin, listArg[0]).group(1)}">Garmin</a>'
            elif re.match(url_pattern, listArg[0]):
                strResult += '<a target="_blank" href="{url}">{url}</a>'.format(url=listArg[0].replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;"))
            else:
                strResult += listArg[0]
            strResult += '</li>\n'
            strResult += '<ul>' + self.getDescriptionHTML(listArg[1]) + '</ul>\n'
        elif type(listArg) is list and listArg:
            # list items
            for c in listArg:
                if type(c) is str and c:
                    strResult += '<li>'
                    if re.match(re_garmin, c):
                        strResult += f'<a target="_blank" href="{prefix_garmin}{re.match(re_garmin, c).group(1)}">Garmin</a>'
                    elif re.match(url_pattern, c):
                        strResult += '<a target="_blank" href="{url}">{url}</a>'.format(url=c.replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;"))
                    else:
                        strResult += c.replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;")
                    strResult += '</li>\n'
                elif type(c) is list:
                    strResult += self.getDescriptionHTML(c)

        return strResult


    def getDescriptionFreemind(self,listArg=None):

        """ returns a Freemind XML string of nested self.description """

        strResult = ''

        if listArg is None:
            strResult += self.getDescriptionFreemind(self.description)
        elif type(listArg) is str and listArg:
            strResult += '<node TEXT="{}"'.format(listArg.replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;"))
            if re.match(url_pattern, listArg):
                strResult += ' LINK="{}"'.format(listArg.replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;"))
            strResult += '/>\n'
        elif type(listArg) is list and len(listArg) == 2 and type(listArg[0]) is str and type(listArg[1]) is list:
            """ tupel (str . list) """

            strResult += '<node FOLDED="{}" TEXT="{}"'.format('true',listArg[0])
            if re.match(url_pattern, listArg[0]):
                strResult += ' LINK="{}"'.format(listArg[0].replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;"))
            strResult += '>\n'

            for c in listArg[1:]:
                strResult += self.getDescriptionFreemind(c)

            strResult += '</node>\n'

        elif type(listArg) is list:
            """ a list, but single element only """
            for c in listArg:
                strResult += self.getDescriptionFreemind(c)

        return strResult


    def getDescriptionXML(self):

        """  """

        return self.getDescriptionString().replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;")


    def getTitleXML(self):

        """  """

        return self.title.replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;")


def _fixIt(listArg=[]):

    """ fix nesting """

    listResult = []

    if type(listArg) is list and len(listArg) == 1 and type(listArg[0]) is list:
        return _fixIt(listArg[0])
    elif type(listArg[0]) is str:
        for e in listArg[1:]:
            if type(e) is list and len(e) == 1 and type(e[0]) is str:
                listResult.append(e[0])
            elif type(e) is list:
                listResult.append(_fixIt(e))

        return [listArg[0],listResult]
    else:
        return listArg


def _appendTo(intDepth=0,listArg=[],strArg=''):

    # search for last element where depth < intDepth => parent list

    l = listArg
    d = 0
    while d < intDepth and type(l[-1]) is list:
        l = l[-1]
        d += 1

    l.append([strArg])


def _flatten(o):

    """ returns a string of nested self.description """

    listResult=[]

    if o is None:
        pass
    elif type(o) is str and o:
        listResult = [o]
    elif type(o) is list and o:
        for c in o:
            if not c:
                pass
            elif type(c) is str:
                listResult.append(c)
            elif type(c) is list:
                listResult.extend(_flatten(c))

    return listResult


