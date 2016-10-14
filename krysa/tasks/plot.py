'''
.. |pyplot| replace:: matplotlib.pyplot
.. _pyplot: http://matplotlib.org/api/pyplot_api.html
'''

from . import Task, LinePlotLayout
from functools import partial
import os.path as op
import numpy as np
import os

# stop stealing Window focus
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot


class Plot(object):
    '''All :ref:`Task` s categorized as `plot` under one roof. To draw plots
    the app uses |pyplot|_ which is automatically dumped to a `*.png` file
    and loaded into result page.

    .. versionadded:: 0.4.3
    '''

    def plot_line(*args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.LinePlotLayout` that
        gets from user :ref:`Data` address. Creates a result page with a plot.

        .. versionadded:: 0.4.3
        '''
        widget = LinePlotLayout()
        task = Task(title='Line plot', wdg=widget,
                    call=['Line plot', Plot.plot_line])
        container = task.ids.container.children[0]
        task.run = partial(Plot._plot_line,
                           task,
                           container.ids.title,
                           container.ids.xname,
                           container.ids.yname,
                           container.ids.labelcheck,
                           container.ids.xlabel,
                           container.ids.ylabel,
                           container.ids.xmin,
                           container.ids.xmax,
                           container.ids.ymin,
                           container.ids.ymax,
                           container.ids.plotcolor,
                           container.ids.plotshape,)
        task.open()

    @staticmethod
    def _plot_line(task, title, xaddress, yaddress, labelcheck,
                   xlabel, ylabel, xmin, xmax, ymin, ymax, plotcolor,
                   plotshape, *args):
        res_dir = op.join(task.app.project_dir, 'plots')
        idx = len([f for f in os.listdir(res_dir) if f.startswith('plot')]) + 1

        # set yvalues to None if input contains only xvalues
        yvalues = None
        if yaddress.text:
            yvalues = task.from_address(task.tablenum, yaddress.text)
        xvalues = task.from_address(task.tablenum, xaddress.text)

        # fetch values
        drawoption = plotcolor.text + plotshape.text
        ylabel = ylabel.text
        xlabel = xlabel.text
        xmin = xmin.text
        xmax = xmax.text
        ymin = ymin.text
        ymax = ymax.text
        axes = []

        # set up plot
        pyplot.hold(False)
        fig = pyplot.figure()
        pyplot.title(title.text)

        # pop the first value to become axis label
        if labelcheck.active:
            xlabel = xvalues[0]
            xvalues = xvalues[1:]
            if yvalues:
                ylabel = yvalues[0]
                yvalues = yvalues[1:]

        # draw either X & Y or X only values
        if yvalues:
            pyplot.plot(xvalues, yvalues, drawoption)
            pyplot.ylabel(ylabel)
            pyplot.xlabel(xlabel)
        else:
            pyplot.plot(xvalues, drawoption)
            pyplot.xlabel(xlabel)

        # check for axis input, use default if empty
        for i, item in enumerate([xmin, xmax, ymin, ymax]):
            if item:
                axes.append(float(item))
            else:
                axes.append(pyplot.axis()[i])

        # dump to file and clean
        pyplot.axis(axes)
        result = op.join(res_dir, 'plot{}.png'.format(idx))
        pyplot.savefig(result)
        pyplot.cla()
        pyplot.clf()
        pyplot.close(fig)

        task.set_page('Line plot', result, 'image')

    names = (('Line plot', plot_line),
             ('_Bar chart', plot_line),
             ('_Pie chart', plot_line))
