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

    def __init__(self,strArg=None,intArg=None):

        """  """


    def getDayDist(self,strArg=None):

        """ lists of distance and time """

        d = [self.dateBegin.toordinal()]
        s = [0.0]

        for u in self.data:
            if (strArg == None or u[3] == strArg) and u[0] > 0 and u[1] > 0.0:
                d.append(u[0])
                s.append(u[1])

        return d, s


    def plotAccumulation(self,fileNameOut=None):

        """ Accumulation chart of periods and cycles """

        strResult = '<pre>not enough data to plot</pre>'

        self.stat()

        # make data
        x = np.array(list(map(lambda lst: lst[0], self.data)))
        x_0 = self.dateBegin.toordinal()
        x_1 = self.dateEnd.toordinal()
        if len(x) > 4:
            # plot:
            fig, ax = plt.subplots()

            ax.grid(visible=True, linestyle='dotted', linewidth=0.5)
            ax.set_xlabel("{} Days".format(x_1 - x_0 + 1))
            ax.set_ylabel(f'Σ [{config.unit_distance}]')
            #ax.set_xticks(np.arange(0, x_1 - x_0, 28))

            for k in sorted(set(map(lambda lst: lst[3], self.data))):
                # one fit per type
                lx, ly = self.getDayDist(k)
                x_n = np.array(lx) - x_0
                # accumulation
                y_a = np.add.accumulate(np.array(ly))

                if len(x_n) != len(y_a):
                    print('error: x and y are no matching data', file=sys.stderr)
                elif len(x_n) < 2:
                    print('info: not enough data for {}'.format(k), file=sys.stderr)
                else:
                    ax.step(x_n, y_a, where='post', label=k)
                    #ax.scatter(x_n, y_a, s=1, label='{}'.format(k))

            plt.legend()

            if fileNameOut == None:
                f = io.StringIO()
                plt.savefig(f, format = "svg")
                plt.close()
                strResult = f.getvalue()
                f.close()
            else:
                plt.savefig(fileNameOut)

        return strResult


    def plotHist(self,fileNameOut=None):

        """ Histogram chart of periods and cycles """

        strResult = '<pre>not enough data to plot</pre>'

        self.stat()

        # make data
        x = np.array(list(map(lambda lst: lst[1], self.data)))
        if len(x) > 2:
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
                strResult = f.getvalue()
                f.close()
            else:
                plt.savefig(fileNameOut)

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

        self.stat()
        if len(self.data) > 0:
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
                strResult = f.getvalue()
                f.close()
            else:
                plt.savefig(fileNameOut)

        return strResult


