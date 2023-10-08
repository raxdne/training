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
#colors = {'Bicycle': '#ffdddd', 'Running': '#ddffdd', 'Swimming': '#ddddff'}
colors = {}

# maximum for length of type string
max_length_type = 20

# distance unit 'mi' or 'km'
unit_distance = 'km'
# default velocity, used in Unit()
v_defaults = {'Bicycle': 25.0, 'Running': 10.0, 'Swimming': 2.0}

#
twilight = 1800
sun = None

# minimum count of data
plot_min = 1

style = """
<style>
    body {font-family: Arial,sans-serif; font-size:12px; margin: 5px 5px 5px 5px;}
    svg {margin: 5px 0;}
    section {border-left: 1px dotted #aaaaaa;}
    section > * {margin: 0px 0px 0px 2px;}
    section > *:not(.header) {margin: 0.5em 0.5em 0.5em 2em;}
    div.header {font-weight:bold;}
    table {border-collapse: collapse; empty-cells:show; margin-left:auto; margin-right:auto; border: 1px solid grey;}
    th, td {padding: 3px}
    td { border: 1px solid grey; vertical-align:top;}
    td.we {background-color: #eeeeee;}
    pre {background-color: #f8f8f8;border: 1px solid #cccccc;padding: 6px 3px;border-radius: 3px;}
    ul, ol {padding: 0px 0px 0px 2em;}
    div > ul {margin-top: 2px; margin-bottom: 3px;}
    a:link {text-decoration:none;}
</style>
"""

def getSettingsStr():

    """ returns a Python string containing all module settings """

    strResult = '# Diagram\n'
    strResult += '{}.diagram_scale_dist = {}\n'.format(__name__, diagram_scale_dist)
    strResult += '{}.diagram_bar_height = {}\n'.format(__name__, diagram_bar_height)
    strResult += '{}.diagram_offset = {}\n'.format(__name__, diagram_offset)
    strResult += '{}.diagram_width = {}\n'.format(__name__, diagram_width)
    strResult += '{}.font_family = {}\n'.format(__name__, font_family)
    strResult += '{}.font_size = {}\n'.format(__name__, font_size)

    strResult += '{}.colors = {}\n'.format(__name__, colors)
    strResult += '{}.max_length_type = {}\n'.format(__name__, max_length_type)
    strResult += '{}.unit_distance = \'{}\'\n'.format(__name__, unit_distance)

    return strResult


