from . import Task, LinePlotLayout
from matplotlib import pyplot
from functools import partial
import os.path as op
import os


class Plot(object):
    '''All :ref:`Task` s categorized as `plot` under one roof.

    .. versionadded:: 0.4.3
    '''

    def plot_line(*args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.LinePlotLayout` that
        gets from user :ref:`Data` address. Creates a result page with plot.

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
                           container.ids.xcheck,
                           container.ids.ycheck,
                           container.ids.xlabel,
                           container.ids.ylabel,
                           container.ids.plotcolor,
                           container.ids.plotshape,)
        task.open()

    @staticmethod
    def _plot_line(task, title, xaddress, yaddress, xcheck, ycheck, xlabel,
                   ylabel, plotcolor, plotshape, *args):
        yvalues = None
        if yaddress.text:
            yvalues = task.from_address(task.tablenum, yaddress.text)
        xvalues = task.from_address(task.tablenum, xaddress.text)
        res_dir = op.join(task.app.project_dir, 'results')
        idx = len([f for f in os.listdir(res_dir) if op.isfile(f)]) + 1

        drawoption = plotcolor.text + plotshape.text
        ylabel = ylabel.text
        xlabel = xlabel.text

        pyplot.hold(False)
        fig = pyplot.figure()
        pyplot.title(title.text)

        if xcheck.active:
            xlabel = xvalues[0]
            xvalues = xvalues[1:]
        if ycheck.active:
            ylabel = yvalues[0]
            yvalues = yvalues[1:]

        if yvalues:
            pyplot.plot(xvalues, yvalues, drawoption)
            pyplot.ylabel(ylabel)
            pyplot.xlabel(xlabel)
        else:
            pyplot.plot(xvalues, drawoption)
            pyplot.xlabel(xlabel)

        result = op.join(res_dir, '{}.png'.format(idx))
        pyplot.savefig(result)
        pyplot.cla()
        pyplot.clf()
        pyplot.close(fig)
        task.set_page('Line plot', result, 'image')

    names = (('Line plot', plot_line),
             ('_Bar chart', plot_line),
             ('_Pie chart', plot_line))
