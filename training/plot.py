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

import io

import sys

import math

from datetime import timedelta, date, datetime, time, timezone

import matplotlib.pyplot as plt
import numpy as np

from training import config as config

#
#
#

class Plot():

    def __init__(self):

        """  """

        #print(f'info: initialize Plot()', file=sys.stderr)
        self.strPlotAccumulation = None
        self.strPlotAccumulationDuration = None
        self.strPlotTimeDist = None
        self.strPlotHist = None


    def setPlot(self,fPlot=False):

        """  """

        if hasattr(self,'child'):
            for c in self.child:
                try:
                    c.setPlot(fPlot)
                except:
                    pass

        self.fPlot = fPlot
        
        return self


    def getDayDist(self,strArg=None):

        """ lists of distance and time """

        d = []
        s = []

        for u in self.data:
            if (strArg == None or u[3] == strArg) and u[0] > 0 and u[1] > 0.0:
                d.append(u[0])
                s.append(u[1])
        
        return d, s


    def plotAccumulation(self,fileNameOut=None):

        """ Accumulation chart of periods and cycles """

        strResult = '<pre>not enough data to plot</pre>'
        
        if (hasattr(self,'child') and len(self.child) > 0) or (hasattr(self,'day') and len(self.day) > 0):

            if self.strPlotAccumulation == None:

                #print(f'info: new plot of "{self.getTitleString()}"', file=sys.stderr)
                self.stat()

                # make data
                x = np.array(list(map(lambda lst: lst[0], self.data)))
                x_0 = self.dateBegin.toordinal()
                x_1 = self.dateEnd.toordinal()
                if len(x) >= config.plot_min:
                    # plot:
                    fig, ax = plt.subplots()

                    ax.grid(visible=True, linestyle='dotted', linewidth=0.5)
                    ax.set_xlabel("{} Days".format(x_1 - x_0 + 1))
                    ax.set_ylabel(f'Σ [{config.unit_distance}]')
                    #ax.set_xticks(np.arange(0, x_1 - x_0, 28))

                    for k in sorted(set(map(lambda lst: lst[3], self.data))):
                        # one fit per type
                        lx, ly = self.getDayDist(k)

                        if len(lx) < 1 or len(lx) != len(ly):
                            print(f'error: x and y are no matching data for "{k}"', file=sys.stderr)
                            continue

                        if lx[0] != x_0:
                            lx.insert(0,x_0)
                            ly.insert(0,0.0)

                        if lx[-1] != x_1:
                            lx.append(x_1)
                            ly.append(0.0)

                        x_n = np.array(lx) - x_0
                        # accumulation
                        y_a = np.add.accumulate(np.array(ly))

                        if len(x_n) != len(y_a):
                            print('error: x and y are no matching data', file=sys.stderr)
                        elif len(x_n) < 2:
                            print(f'info: not enough data for {k}', file=sys.stderr)
                        else:
                            ax.step(x_n, y_a, where='post', label=k)
                            #ax.scatter(x_n, y_a, s=1, label=k)

                    # plot today as vertical line
                    x_nt = date.today().toordinal() - x_0
                    if x_nt >= 0 and x_nt <= (x_1 - x_0):
                        plt.axvline(x=x_nt, color='#ff0000', linewidth=0.5)

                    plt.legend()

                    if fileNameOut == None:
                        f = io.StringIO()
                        plt.savefig(f, format = "svg")
                        plt.close()
                        self.strPlotAccumulation = f.getvalue()
                        f.close()
                    else:
                        plt.savefig(fileNameOut)

            elif len(self.strPlotAccumulation) > 0:
                print(f'info: re-using plot of "{self.getTitleString()}"', file=sys.stderr)

            if self.strPlotAccumulation != None:
                strResult = self.strPlotAccumulation
                # TODO: write self.strPlotAccumulation to fileNameOut

        return strResult


    def getDayDuration(self,strArg=None):

        """ lists of duration and time """

        d = []
        s = []

        for u in self.data:
            if (strArg == None or u[3] == strArg) and u[0] > 0 and u[2] > 0.0:
                d.append(u[0])
                s.append(u[2] / 60.0)
        
        return d, s


    def plotAccumulationDuration(self,fileNameOut=None):

        """ Accumulation chart of periods and cycles """

        strResult = '<pre>not enough data to plot</pre>'

        if (hasattr(self,'child') and len(self.child) > 0) or (hasattr(self,'day') and len(self.day) > 0):

            if self.strPlotAccumulationDuration == None:

                #print(f'info: new plot of "{self.getTitleString()}"', file=sys.stderr)
                self.stat()
                # make data
                x = np.array(list(map(lambda lst: lst[0], self.data)))
                x_0 = self.dateBegin.toordinal()
                x_1 = self.dateEnd.toordinal()
                if len(x) >= config.plot_min:
                    # plot:
                    fig, ax = plt.subplots()

                    ax.grid(visible=True, linestyle='dotted', linewidth=0.5)
                    ax.set_xlabel("{} Days".format(x_1 - x_0 + 1))
                    ax.set_ylabel(f'Σ [h]')
                    #ax.set_xticks(np.arange(0, x_1 - x_0, 28))

                    lx, ly = self.getDayDuration()

                    if len(lx) < 1 or len(lx) != len(ly):
                        print('error: x and y are no matching data', file=sys.stderr)
                        return strResult

                    if lx[0] != x_0:
                        lx.insert(0,x_0)
                        ly.insert(0,0.0)

                    if lx[-1] != x_1:
                        lx.append(x_1)
                        ly.append(0.0)

                    x_n = np.array(lx) - x_0
                    # accumulation
                    y_a = np.add.accumulate(np.array(ly))

                    if len(x_n) != len(y_a):
                        print('error: x and y are no matching data', file=sys.stderr)
                    elif len(x_n) < 2:
                        print(f'info: not enough data', file=sys.stderr)
                    else:
                        ax.step(x_n, y_a, where='post', label='Duration')
                        #ax.scatter(x_n, y_a, s=1, label=k)

                    # plot today as vertical line
                    x_nt = date.today().toordinal() - x_0
                    if x_nt >= 0 and x_nt <= (x_1 - x_0):
                        plt.axvline(x=x_nt, color='#ff0000', linewidth=0.5)

                    plt.legend()

                    if fileNameOut == None:
                        f = io.StringIO()
                        plt.savefig(f, format = "svg")
                        plt.close()
                        self.strPlotAccumulationDuration = f.getvalue()
                        f.close()
                    else:
                        plt.savefig(fileNameOut)
            elif len(self.strPlotAccumulationDuration) > 0:
                # use existing plot
                print(f'info: re-using plot of "{self.getTitleString()}"', file=sys.stderr)

            if self.strPlotAccumulationDuration != None:
                strResult = self.strPlotAccumulationDuration
                # TODO: write self.strPlotAccumulationDuration to fileNameOut
            
        return strResult


    def plotHist(self,fileNameOut=None):

        """ Histogram chart of periods and cycles """

        strResult = '<pre>not enough data to plot</pre>'

        if (hasattr(self,'child') and len(self.child) > 0) or (hasattr(self,'day') and len(self.day) > 0):

            if self.strPlotHist == None:

                #print(f'info: new plot of "{self.getTitleString()}"', file=sys.stderr)
                self.stat()

                # make data
                x = np.array(list(map(lambda lst: lst[1], self.data)))
                if len(x) >= config.plot_min:
                    # plot:
                    fig, ax = plt.subplots()
                    b = np.arange(0.01, 151, 5)
                    ax.grid(visible=True, linestyle='dotted', linewidth=0.5)
                    ax.hist(x, bins=b, linewidth=0.5, edgecolor="white", label='{} Units'.format(len(x)))
                    ax.set_xlabel(f's [{config.unit_distance}]')
                    ax.set_ylabel("n")
                    #plt.bar_label(bars, fontsize=20, color='navy')
                    #for v in b:
                    #    plt.text(x=v,y=5,s=v)

                    plt.legend()

                    if fileNameOut == None:
                        f = io.StringIO()
                        plt.savefig(f, format = "svg")
                        plt.close()
                        self.strPlotHist = f.getvalue()
                        f.close()
                    else:
                        plt.savefig(fileNameOut)
            elif len(self.strPlotHist) > 0:
                # use existing plot
                print(f'info: re-using plot of "{self.getTitleString()}"', file=sys.stderr)

            if self.strPlotHist != None:
                strResult = self.strPlotHist
                # TODO: write self.strPlotHist to fileNameOut

        return strResult



    def getTimeDist(self,strArg=None):

        """ lists of distance and time """

        s = []
        t = []

        for u in self.data:
            if (strArg == None or u[3] == strArg) and u[1] > 0.0 and u[2] > 0.0:
                s.append(u[1])
                t.append(u[2])

        return s, t


    def plotTimeDist(self,fileNameOut=None):

        """ chart of time over distance """

        # TODO: https://matplotlib.org/stable/gallery/lines_bars_and_markers/scatter_hist.html

        strResult = '<pre>not enough data to plot</pre>'

        if (hasattr(self,'child') and len(self.child) > 0) or (hasattr(self,'day') and len(self.day) > 0):

            if self.strPlotTimeDist == None:

                #print(f'info: new plot of "{self.getTitleString()}"', file=sys.stderr)
                self.stat()
                if len(self.data) >= config.plot_min:
                    # plot:

                    fig, ax = plt.subplots()

                    #ax.set_xticks(np.arange(0, 151, 5), minor=True)
                    ax.set_xticks(np.arange(0, 151, 25))

                    #ax.set_yticks(np.arange(0, 301, 15), minor=True)
                    ax.set_yticks(np.arange(0, 451, 30))

                    ax.grid(visible=True, linestyle='dotted', linewidth=0.5)

                    # Plot a curved line with ticked style path
                    x_l = np.array([0.0, 40.0])
                    y_l = x_l * 6.0
                    ax.plot(x_l, y_l, linestyle='dotted', label=f"v=10 {config.unit_distance}/h")
                    x_l = np.array([0.0, 151.0])
                    y_l = x_l * 3.0
                    ax.plot(x_l, y_l, linestyle='dotted', label=f"v=20 {config.unit_distance}/h")
                    y_l = x_l * 2.0
                    ax.plot(x_l, y_l, linestyle='dotted', label=f"v=30 {config.unit_distance}/h")

                    ax.set_xlabel(f's [{config.unit_distance}]')
                    ax.set_ylabel("t [min]")

                    for k in sorted(set(map(lambda lst: lst[3], self.data))):
                        # one fit per type

                        lx, ly = self.getTimeDist(k)
                        x = np.array(lx)
                        y = np.array(ly)
                        if len(x) != len(y):
                            print('error: x and y are no matching data', file=sys.stderr)
                            continue

                        ax.scatter(x, y, s=4)

                        if len(x) < 1:
                            continue
                        elif True:
                            m_y = np.mean(y)
                            m_x = np.mean(x)
                            ax.vlines(m_x,0,m_y)
                            d_y = m_y / m_x
                            x_f = np.array([0.0, 1.25 * np.max(x)])
                            y_f = d_y * x_f
                            if d_y > 3.5:
                                ax.plot(x_f, y_f, label="{}: {} Units, t∅ = {}:{:02} min/{}".format(k, len(x), int(d_y), int((d_y - int(d_y)) * 60), config.unit_distance))
                            else:
                                ax.plot(x_f, y_f, label="{}: {} Units, v∅ = {} {}/h".format(k, len(x), round(60.0 / d_y,1), config.unit_distance))
                        else:
                            z = np.polyfit(x, y, 1)
                            if z[0] > 0.0 and z[0] < 10.0:
                                y_f = z[0] * x + z[1]
                                ax.plot(x, y_f, label="t({},s) = {:.1f} * s + {:.1f}".format(k,z[0],z[1]))

                    ax.legend()

                    #plt.show()

                    if fileNameOut == None:
                        f = io.StringIO()
                        plt.savefig(f, format = "svg")
                        plt.close()
                        self.strPlotTimeDist = f.getvalue()
                        f.close()
                    else:
                        plt.savefig(fileNameOut)
            elif len(self.strPlotTimeDist) > 0:
                # use existing plot
                print(f'info: re-using plot of "{self.getTitleString()}"', file=sys.stderr)

            if self.strPlotTimeDist != None:
                strResult = self.strPlotTimeDist
                # TODO: write self.strPlotTimeDist to fileNameOut

        return strResult


    def toSVGGanttBar(self,dateBase,y=0):

        """ returns SVG string of vertical and horizontal bars in Gantt Chart """

        flagHBar = False
        flagVBar = True
        
        if hasattr(self,'day'):
            # it's a Cycle
            if self.day == None:
                print('error: empty ' + str(type(self)), file=sys.stderr)
                return ''
            elif len(self.day) > 0:
                l = self.getPeriodDone()
                flagHBar = True
            else:
                print('error: YYY', file=sys.stderr)
                return ''
        elif hasattr(self,'child'):
            # it's a Period
            l = (self.dateEnd - self.dateBegin).days + 1
            flagVBar = len(self.child) < 1
        else:
            print('error: unknown type ' + str(type(self)), file=sys.stderr)
            return ''

        # TODO: make config.diagram_height configurable
        config.diagram_height = 40 * (config.diagram_bar_height * 2) + 100

        x_i = (self.dateBegin - dateBase).days * 2

        strResult = '<g>'

        if flagHBar:
            
            # horizontal bar

            if self.color == None:
                color = '#ffaaaa'
            else:
                color = self.color

            strResult += '<a href="#{}">'.format(str(id(self)))
            strResult += '<rect opacity=".75" stroke="red" stroke-width=".5" fill="{}" x="{}" y="{}" height="{}" width="{}" rx="2">\n'.format(color, x_i, y, config.diagram_bar_height*2, len(self) * 2)
            strResult += '<title>{}</title>\n'.format(self.getTitleXML() + self.getDateString() + ' ' + self.getDescriptionString())
            strResult += '</rect>'
            strResult += '</a>'

        if flagVBar:

            # vertical bar

            h = round(self.getDuration().total_seconds() / 60 / l)

            if self.color != None:
                scolor = 'red'
                color = self.color
            elif h > 20:
                scolor = 'green'
                color = '#aaffaa'
            elif h > 4:
                scolor = 'red'
                color = '#ffaaaa'
            else:
                h = 2
                scolor = 'red'
                color = 'red'

            strResult += '<a href="#{}">'.format(str(id(self)))
            strResult += '<rect opacity=".75" stroke="{}" stroke-width=".5" fill="{}" x="{}" y="{}" height="{}" width="{}">\n'.format(scolor, color, x_i + 1, config.diagram_height - h - 10, h, l * 2 - 2)
            strResult += '<title>{}</title>\n'.format(self.getTitleXML() + self.getDateString() + '\n\n' + self.getDescriptionString() + '\n\n' + self.report())
            strResult += '</rect>'
            strResult += '</a>'

        #strResult += '<text x="{}" y="{}">{}</text>\n'.format(x_i,y,self.getTitleXML())
        strResult += '</g>'

        return strResult


