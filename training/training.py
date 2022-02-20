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

