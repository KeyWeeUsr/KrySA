'''
.. |b| replace:: bins
.. _b: http://docs.scipy.org/doc/numpy/reference/generated/numpy.histogram.html
'''

from . import Task, AddressLayout, SmallLargeLayout, FreqLayout
from functools import partial
from numpy import histogram
import math


class Basic(object):
    '''All :ref:`Task` s categorized as `basic` under one roof.

    .. versionadded:: 0.1.0
    '''

    def basic_count(*args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.AddressLayout` that
        gets from user :ref:`Data` address.

        .. versionadded:: 0.1.0
        '''
        widget = AddressLayout()
        task = Task(title='Count', wdg=widget,
                    call=['Count', Basic.basic_count])
        task.run = partial(Basic._basic_count,
                           task,
                           task.ids.container.children[0].ids.name)
        task.open()

    @staticmethod
    def _basic_count(task, address, *args):
        '''Gets the values from address and returns the count.

        .. versionadded:: 0.1.0
        '''
        values = task.from_address(task.tablenum, address.text)
        task.set_page('Count', str(len(values)), 'text')

    def basic_countifs(self, *args):
        '''Not yet implemented.
        '''

    def basic_min(*args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.AddressLayout` that
        gets from user :ref:`Data` address.

        .. versionadded:: 0.1.0
        '''
        widget = AddressLayout()
        task = Task(title='Minimum', wdg=widget,
                    call=['Minimum', Basic.basic_min])
        task.run = partial(Basic._basic_min,
                           task,
                           task.ids.container.children[0].ids.name)
        task.open()

    @staticmethod
    def _basic_min(task, address, *args):
        '''Gets the values from address and returns a minimum.

        .. versionadded:: 0.1.0
        '''
        values = task.from_address(task.tablenum, address.text)
        task.set_page('Minimum', str(min(values)), 'text')

    def basic_max(*args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.AddressLayout` that
        gets from user :ref:`Data` address.

        .. versionadded:: 0.1.0
        '''
        widget = AddressLayout()
        task = Task(title='Maximum', wdg=widget,
                    call=['Maximum', Basic.basic_max])
        task.run = partial(Basic._basic_max,
                           task,
                           task.ids.container.children[0].ids.name)
        task.open()

    @staticmethod
    def _basic_max(task, address, *args):
        '''Gets the values from address and returns a maximum.

        .. versionadded:: 0.1.0
        '''
        values = task.from_address(task.tablenum, address.text)
        task.set_page('Maximum', str(max(values)), 'text')

    def basic_small(*args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.SmallLargeLayout` that
        gets from user :ref:`Data` address and `k` variable representing the
        `k`-th value from the :ref:`Task` s output.

        .. versionadded:: 0.1.0
        '''
        widget = SmallLargeLayout()
        task = Task(title='Small', wdg=widget,
                    call=['Small', Basic.basic_small])
        task.run = partial(Basic._basic_small,
                           task,
                           task.ids.container.children[0].ids.name,
                           task.ids.container.children[0].ids.order)
        task.open()

    @staticmethod
    def _basic_small(task, address, k, *args):
        '''Gets the values from address and returns the `k`-th value from
        the ascending list of sorted values.

        .. versionadded:: 0.1.0
        '''
        values = task.from_address(task.tablenum, address.text)
        values = sorted(values)
        k = int(k.text) - 1
        try:
            task.set_page('Small ({}.)'.format(k + 1), str(values[k]), 'text')
        except IndexError:
            pass

    def basic_large(self, *args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.SmallLargeLayout` that
        gets from user :ref:`Data` address and `k` variable representing the
        `k`-th value from the :ref:`Task` s output.

        .. versionadded:: 0.1.0
        '''
        widget = SmallLargeLayout()
        task = Task(title='Large', wdg=widget,
                    call=['Large', Basic.basic_large])
        task.run = partial(Basic._basic_large,
                           task,
                           task.ids.container.children[0].ids.name,
                           task.ids.container.children[0].ids.order)
        task.open()

    @staticmethod
    def _basic_large(task, address, k, *args):
        '''Gets the values from address and returns the `k`-th value from
        the descending list of sorted values.

        .. versionadded:: 0.1.0
        '''
        values = task.from_address(task.tablenum, address.text)
        values = sorted(values, reverse=True)
        k = int(k.text) - 1
        try:
            task.set_page('Large ({}.)'.format(k + 1), str(values[k]), 'text')
        except IndexError:
            pass  # throw error k out of len(values) bounds, same for *_small

    def basic_freq(self, *args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.FreqLayout` that
        gets from user:

        * :ref:`data` address
        * type of frequency (`absolute`, `relative` or `cumulative`
        * |b|_
        * lower and upper limit (optional, by default takes `min` and `max`)

        .. versionadded:: 0.3.2
        .. versionchanged:: 0.3.8
           Switched to NumPy's `histogram` which is more flexible.
        '''
        widget = FreqLayout()
        task = Task(title='Frequency', wdg=widget,
                    call=['Frequency', Basic.basic_freq])
        task.run = partial(
            Basic._basic_freq,
            task,
            task.ids.container.children[0].ids.name,
            (task.ids.container.children[0].ids.binmanager,
             task.ids.container.children[0].ids.bins,
             task.ids.container.children[0].ids.bingrid,
             task.ids.container.children[0].ids.binstr),
            (task.ids.container.children[0].ids.lowlimit,
             task.ids.container.children[0].ids.uplimit,
             task.ids.container.children[0].ids.limits_auto),
            (task.ids.container.children[0].ids.absolute,
             task.ids.container.children[0].ids.relative,
             task.ids.container.children[0].ids.cumulative))
        task.open()

    @staticmethod
    def _basic_freq(task, address, bins, limits, freq_type, *args):
        '''Gets the values from address and depending on the inputed bins:

        * `Count` of equal-width bins
        * `Edges` manually created edges for non-uniform bin widths. It already
          contains minimum and maximum of the values list.
        * `Calculate` uses NumPy's way for creating an optimal bin width.

        Then according to the size of bins and limits of the frequency creates
        a table for chosen types of frequency.

        .. versionadded:: 0.3.2
        .. versionchanged:: 0.3.8
           Switch from SciPy's frequency functions to NumPy's `histogram` which
           removes `intervals` option as this is already handled by histogram.
        '''

        # input variables
        bin_type, bins, bingrid, binstr = bins
        lowlimit, uplimit, limits_auto = limits
        absolute, relative, cumulative = freq_type

        # setting variables
        values = task.from_address(task.tablenum, address.text)
        values = [float(val) for val in values]
        values = sorted(values)
        cols = 2

        if limits_auto.active:
            lowlimit = min(values)
            uplimit = max(values)
        else:
            lowlimit = float(lowlimit.text)
            uplimit = float(uplimit.text)

        # get either int of bins or float list of edges
        bin_type = bin_type.current
        if bin_type == 'Count':
            bins = int(bins.text)
        elif bin_type == 'Edges':
            bins = [float(child.text) for child in bingrid.children]
            bins = sorted(bins)
            if bins[0] > min(values):
                bins = [min(values)] + bins
            if bins[-1] < max(values):
                bins = bins + [max(values)]
        elif bin_type == 'Calculate':
            bins = binstr.su

        # get base for results
        histo, edges = histogram(values, bins=bins, range=(lowlimit, uplimit))
        values_len = float(len(values))

        # set edge values
        left = []
        right = []
        for i in xrange(len(edges)):
            left.append(edges[i])
            try:
                right.append(edges[i+1])
            except IndexError:
                right.append('-')

        # "float(val)" to convert from numpy's type
        absol = []
        if absolute.active:
            absol = [float(val) for val in histo]
            absol.insert(0, 'Absolute')
            cols += 1

        relat = []
        if relative.active:
            relat = [float(val) / values_len for val in histo]
            relat.insert(0, 'Relative')
            cols += 1

        cumul = []
        if cumulative.active:
            if not relative.active:
                _relat = [float(val) / values_len for val in histo]
            else:
                _relat = relat[1:]

            previous = 0
            for i in xrange(len(histo)):
                cumul.append(previous + float(_relat[i]))
                previous += float(_relat[i])
            cumul.insert(0, 'Cumulative')
            cols += 1

        # zipping & exporting results
        rs = []
        left.insert(0, 'Lower edge')
        right.insert(0, 'Upper edge')

        if absol and not relat and not cumul:
            rs = [r for items in zip(left, right, absol) for r in items]
        elif absol and relat and not cumul:
            rs = [r for items in zip(left, right, absol, relat) for r in items]
        elif absol and cumul and not relat:
            rs = [r for items in zip(left, right, absol, cumul) for r in items]
        elif relat and not absol and not cumul:
            rs = [r for items in zip(left, right, relat) for r in items]
        elif relat and cumul and not absol:
            rs = [r for items in zip(left, right, relat, cumul) for r in items]
        elif cumul and not absol and not relat:
            rs = [r for items in zip(left, right, cumul) for r in items]
        elif absol and relat and cumul:
            zipped = zip(left, right, absol, relat, cumul)
            rs = [r for items in zipped for r in items]

        task.set_page('Frequency', rs, 'table{}'.format(cols))

    names = (('Count', basic_count),
             ('_Count ifs', basic_countifs),
             ('Minimum', basic_min),
             ('Maximum', basic_max),
             ('Small', basic_small),
             ('Large', basic_large),
             ('Frequency', basic_freq))
