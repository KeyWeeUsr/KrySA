'''
.. |b| replace:: bins
.. _b: http://docs.scipy.org/doc/numpy/reference/generated/numpy.histogram.html
'''

from . import Task, AddressLayout, SmallLargeLayout, FreqLayout, CountIfLayout
from functools import partial
from numpy import histogram
import math


# Py3 fixes
import sys
if sys.version_info[0] >= 3:
    unicode = str
    str = bytes
    xrange = range


class Basic(object):
    '''All :ref:`Task` s categorized as `basic` under one roof.

    .. versionadded:: 0.1.0
    '''

    def basic_count(*args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.AddressLayout` that
        gets from user :ref:`Data` address. Creates a result page with count.

        .. versionadded:: 0.1.0
        '''
        widget = AddressLayout()
        task = Task(title='Count', wdg=widget,
                    call=['Count', Basic.basic_count])
        container = task.ids.container.children[0]
        task.run = partial(Basic._basic_count,
                           task,
                           container.ids.name)
        task.open()

    @staticmethod
    def _basic_count(task, address, *args):
        values = task.from_address(task.tablenum, address.text)
        task.set_page('Count', unicode(len(values)), 'text')

    def basic_countif(self, *args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.CountIfLayout` that
        gets from user :ref:`Data` address and conditions for getting values.
        Creates a result page with count.

        This method uses Python's `eval()` and executing of boolean logic,
        which means the order of executed conditions will be like this::

            ((Cond and Cond) and Cond) or (Cond) or (Cond and Cond)
              ^-- first   second --^       ^-- third   ^-- fourth

        .. versionadded:: 0.5.1
        '''
        widget = CountIfLayout()
        task = Task(title='Count If', wdg=widget,
                    call=['Count If', Basic.basic_countif])
        container = task.ids.container.children[0]
        task.run = partial(Basic._basic_countif,
                           task,
                           container.ids.name,
                           container.ids.conditions)
        task.open()

    @staticmethod
    def _basic_countif(task, address, conditions, *args):
        values = task.from_address(task.tablenum, address.text)
        result = ''
        instruction = ''
        count = 0

        groups = []
        grp = []
        for child in reversed(conditions.children):
            operation = child.children[-1].text
            op_val = child.children[-2].text
            logic = child.children[-3].text
            if operation != '---' and op_val:
                grp.append([operation, op_val])
            if logic == '---':
                groups.append(grp)
                break
            if logic == 'OR':
                groups.append(grp)
                grp = []

        for i, grp in enumerate(groups):
            for g in grp:
                vals = []
                operation = g[0]
                op_val = g[1]
                last_op = instruction[-5:]
                if last_op != ' and ' and ' or ' not in last_op and last_op:
                    instruction += ' and '
                if operation == 'Less than':
                    instruction += 'val < '
                elif operation == 'Less than or equal':
                    instruction += 'val <= '
                elif operation == 'Greater than':
                    instruction += 'val > '
                elif operation == 'Greater than or equal':
                    instruction += 'val >= '
                elif operation == 'Equal to':
                    instruction += 'val == '
                elif operation == 'Not equal to':
                    instruction += 'val != '
                instruction += op_val
                result += operation + ' ' + op_val + '\n'
            try:
                groups[i + 1]
                instruction += ' or '
            except IndexError:
                pass

        for val in values:
            if eval(instruction):
                count += 1

        result += '\nCount: ' + unicode(count)
        task.set_page('Count If', result, 'text')

    def basic_min(*args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.AddressLayout` that
        gets from user :ref:`Data` address. Creates a result page with minimum.

        .. versionadded:: 0.1.0
        '''
        widget = AddressLayout()
        task = Task(title='Minimum', wdg=widget,
                    call=['Minimum', Basic.basic_min])
        container = task.ids.container.children[0]
        task.run = partial(Basic._basic_min,
                           task,
                           container.ids.name)
        task.open()

    @staticmethod
    def _basic_min(task, address, *args):
        values = task.from_address(task.tablenum, address.text)
        task.set_page('Minimum', unicode(min(list(set(values)))), 'text')

    def basic_max(*args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.AddressLayout` that
        gets from user :ref:`Data` address. Creates a result page with maximum.

        .. versionadded:: 0.1.0
        '''
        widget = AddressLayout()
        task = Task(title='Maximum', wdg=widget,
                    call=['Maximum', Basic.basic_max])
        container = task.ids.container.children[0]
        task.run = partial(Basic._basic_max,
                           task,
                           container.ids.name)
        task.open()

    @staticmethod
    def _basic_max(task, address, *args):
        values = task.from_address(task.tablenum, address.text)
        task.set_page('Maximum', unicode(max(list(set(values)))), 'text')

    def basic_small(*args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.SmallLargeLayout` that
        gets from user :ref:`Data` address and `k` variable representing the
        `k`-th value from the :ref:`Task` s output. Creates a result page with
        the `k`-th value.

        .. versionadded:: 0.1.0
        '''
        widget = SmallLargeLayout()
        task = Task(title='Small', wdg=widget,
                    call=['Small', Basic.basic_small])
        container = task.ids.container.children[0]
        task.run = partial(Basic._basic_small,
                           task,
                           container.ids.name,
                           container.ids.order)
        task.open()

    @staticmethod
    def _basic_small(task, address, k, *args):
        values = task.from_address(task.tablenum, address.text)
        values = sorted(list(set(values)))
        k = int(k.text) - 1
        try:
            task.set_page('Small ({}.)'.format(k + 1),
                          unicode(values[k]), 'text')
        except IndexError:
            pass

    def basic_large(self, *args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.SmallLargeLayout` that
        gets from user :ref:`Data` address and `k` variable representing the
        `k`-th value from the :ref:`Task` s output. Creates a result page with
        `k`-th value.

        .. versionadded:: 0.1.0
        '''
        widget = SmallLargeLayout()
        task = Task(title='Large', wdg=widget,
                    call=['Large', Basic.basic_large])
        container = task.ids.container.children[0]
        task.run = partial(Basic._basic_large,
                           task,
                           container.ids.name,
                           container.ids.order)
        task.open()

    @staticmethod
    def _basic_large(task, address, k, *args):
        values = task.from_address(task.tablenum, address.text)
        values = sorted(list(set(values)), reverse=True)
        k = int(k.text) - 1
        try:
            task.set_page('Large ({}.)'.format(k + 1),
                          unicode(values[k]), 'text')
        except IndexError:
            pass  # throw error k out of len(values) bounds, same for *_small

    def basic_freq(self, *args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.FreqLayout` that
        gets from user:

        * :ref:`data` address
        * type of frequency (`absolute`, `relative` or `cumulative`
        * |b|_
        * lower and upper limit (optional, by default takes `min` and `max`)

        Depending on the inputed bins:

        * `Count` of equal-width bins
        * `Edges` manually created edges for non-uniform bin widths. It already
          contains minimum and maximum of the values list.
        * `Calculate` uses NumPy's way for creating an optimal bin width.

        The function creates a result page with a table for chosen types of
        frequency. If necessary, you can set the maximal amount of decimal
        digits for the frequency outputs.

        .. versionadded:: 0.3.2
        .. versionchanged:: 0.3.8
           Switch from SciPy's frequency functions to NumPy's `histogram` which
           removes `intervals` option as this is already handled by histogram.
        .. versionchanged:: 0.3.9
           Added precision.
        '''

        widget = FreqLayout()
        task = Task(title='Frequency', wdg=widget,
                    call=['Frequency', Basic.basic_freq])
        container = task.ids.container.children[0]
        task.run = partial(
            Basic._basic_freq,
            task,
            container.ids.name,
            container.ids.precision,
            (container.ids.binmanager, container.ids.bins,
             container.ids.bingrid, container.ids.binstr),
            (container.ids.lowlimit, container.ids.uplimit,
             container.ids.limits_auto),
            (container.ids.absolute, container.ids.relative,
             container.ids.cumulative))
        task.open()

    @staticmethod
    def _basic_freq_prec(input_list, precision, *args):
        if precision == '':
            return input_list
        try:
            precision = int(precision)
        except ValueError:
            raise Exception('Bad precision input!')

        final = []
        if precision:
            for item in input_list:
                if isinstance(item, (str, unicode)):
                    final.append(item)
                else:
                    final.append(round(item, precision))
        return final

    @staticmethod
    def _basic_freq(task, address, precision, bins, limits, freq_type, *args):
        # input variables
        bin_type, bins, bingrid, binstr = bins
        lowlimit, uplimit, limits_auto = limits
        absolute, relative, cumulative = freq_type
        precision = precision.text

        # setting variables
        values = task.from_address(task.tablenum, address.text)
        values = [float(val) for val in values]
        values = sorted(values)
        cols = 2

        if limits_auto.active:
            lowlimit = min(values)
            uplimit = max(values)
        else:
            if lowlimit.text and uplimit.text:
                lowlimit = float(lowlimit.text)
                uplimit = float(uplimit.text)
            else:
                raise Exception(
                    'Manual limits enabled! '
                    'You need to enter both lower and upper limit.')

        # get either int of bins or float list of edges
        bin_type = bin_type.current
        if bin_type == 'Count':
            if bins.text:
                bins = int(bins.text)
            else:
                raise Exception('No count of bins entered!')
        elif bin_type == 'Edges':
            bins = [float(child.text) for child in bingrid.children]
            bins = sorted(bins)
            if bins[0] > min(values):
                bins.insert(0, min(values))
            if bins[-1] < max(values):
                bins.extend([max(values)])
        elif bin_type == 'Calculate':
            bins = binstr.value

        # get base for results
        histo, edges = histogram(values, bins=bins, range=(lowlimit, uplimit))
        values_len = float(len(values))

        # set edge values
        left = []
        right = []
        for i in xrange(len(edges)):
            left.append(float(edges[i]))
            try:
                right.append(float(edges[i + 1]))
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
            if absol:
                relat = [val / values_len for val in absol[1:]]
            else:
                relat = [float(val) / values_len for val in histo]
            relat = Basic._basic_freq_prec(relat, precision)
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
            cumul = Basic._basic_freq_prec(cumul, precision)
            cumul.insert(0, 'Cumulative')
            cols += 1

        # zipping & exporting results
        left = Basic._basic_freq_prec(left, precision)
        right = Basic._basic_freq_prec(right, precision)
        left.insert(0, 'Lower edge')
        right.insert(0, 'Upper edge')

        if absol and not relat and not cumul:
            zipped = zip(left, right, absol)
        elif absol and relat and not cumul:
            zipped = zip(left, right, absol, relat)
        elif absol and cumul and not relat:
            zipped = zip(left, right, absol, cumul)
        elif relat and not absol and not cumul:
            zipped = zip(left, right, relat)
        elif relat and cumul and not absol:
            zipped = zip(left, right, relat, cumul)
        elif cumul and not absol and not relat:
            zipped = zip(left, right, cumul)
        elif absol and relat and cumul:
            zipped = zip(left, right, absol, relat, cumul)

        result = [r for items in zipped for r in items]
        bin_type = binstr.text if 'Calc' in bin_type else bin_type
        bins = ', bins=' + unicode(bins) if 'Count' in bin_type else ''
        params = '{}{}'.format(bin_type, bins)
        task.set_page('Frequency({})'.format(params),
                      result, 'table{}'.format(cols))

    names = (('Count', basic_count),
             ('Count If', basic_countif),
             ('Minimum', basic_min),
             ('Maximum', basic_max),
             ('Small', basic_small),
             ('Large', basic_large),
             ('Frequency', basic_freq))
