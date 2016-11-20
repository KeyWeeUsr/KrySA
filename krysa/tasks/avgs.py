from . import Task, AvgsLayout, AddressLayout
from functools import partial, reduce
from collections import Counter
import operator
import math


class Avgs(object):
    '''All :ref:`Task` s categorized as `averages` under one roof.

    .. versionadded:: 0.2.4
    '''

    def avgs_gen(*args):
        '''Get the values from address and depending on `p` (power) value
        returns either exceptional case for `p == 0` (geometric mean), or
        a value from the generalized mean's formula:

        .. math::
           \\big(\\frac{1}{n}\\sum_{i=1}^n  x_{i}^{p} \\big)^\\frac{1}{p},
           where:

        * p == -1: harmonic
        * p == 0: geometric
        * p == 1: arithmetic
        * p == 2: quadratic
        * p == 3: cubic
        * etc...

        .. versionadded:: 0.2.4
        '''
        widget = AvgsLayout()
        task = Task(title='Count', wdg=widget,
                    call=['Count', Avgs.avgs_gen])
        container = task.ids.container.children[0]
        task.run = partial(Avgs._avgs_gen,
                           task,
                           container.ids.name,
                           container.ids.power)
        task.open()

    @staticmethod
    def _avgs_gen(task, address, p, *args):
        if p == '-0':
            p = 0.0
        else:
            p = float(p.text)

        values = task.from_address(task.tablenum, address.text)
        if p in [0, -0]:
            multiples = reduce(operator.mul, values, 1)
            result = math.pow(multiples, 1 / float(len(values)))
            p = 'geometric'
        else:
            values = [math.pow(val, p) for val in values]
            upper = math.fsum(values) / float(len(values))
            result = math.pow(upper, 1 / float(p))
        task.set_page('Generalized mean({})'.format(p), str(result), 'text')

    def avgs_inter(*args):
        '''(Not yet implemented)
        '''

    def avgs_mid(*args):
        '''(Not yet implemented)
        '''

    def avgs_trim(*args):
        '''(Not yet implemented)
        '''

    def avgs_median(*args):
        '''Median:

        .. math::
            \\tilde x = \\left \\{ \\begin {array}{lr}
                \\frac {n}{2} \in \\mathbb{N}:&
                    \\frac {x_{\\frac {n}{2}} + x_{\\frac {n}{2}+1}}{2}
                \\\\
                \\frac {n+1}{2} \in \\mathbb{N}:&
                    x_{\\lceil \\frac {n}{2} \\rceil}
            \\end{array} \\right.

        .. versionadded:: 0.3.10
        '''
        widget = AddressLayout()
        task = Task(title='Median', wdg=widget,
                    call=['Median', Avgs.avgs_median])
        container = task.ids.container.children[0]
        task.run = partial(Avgs._avgs_median,
                           task,
                           container.ids.name)
        task.open()

    @staticmethod
    def _avgs_median(task, address, *args):
        values = task.from_address(task.tablenum, address.text)
        length = len(values)
        pos = int(round(length / 2.0))
        if length == 1:
            result = values[0]
        elif length % 2:
            result = values[pos - 1]
        else:
            result = int(values[pos - 1] + values[pos]) / 2.0
        task.set_page('Median', str(result), 'text')

    def avgs_mode(*args):
        '''Return the most common value from the list of values.
        If there's more than a single value with the same amount of
        occurency, all values with the same occurency are returned.

        .. versionadded:: 0.3.10
        '''
        widget = AddressLayout()
        task = Task(title='Mode', wdg=widget,
                    call=['Mode', Avgs.avgs_mode])
        container = task.ids.container.children[0]
        task.run = partial(Avgs._avgs_mode,
                           task,
                           container.ids.name)
        task.open()

    @staticmethod
    def _avgs_mode(task, address, *args):
        values = task.from_address(task.tablenum, address.text)
        length = len(values)
        data = Counter(values)
        occurs = data.most_common(length)
        results = []
        for oc in occurs:
            if not results:
                results.append(oc)
            else:
                if results[-1][1] == oc[1]:
                    results.append(oc)
        results = [str(r[0]) for r in results]
        task.set_page('Mode', ', '.join(results), 'text')

    names = (('Generalized', avgs_gen),
             ('_Interquartile', avgs_inter),
             ('_Midrange', avgs_mid),
             ('_Trimmed', avgs_trim),
             ('Median', avgs_median),
             ('Mode', avgs_mode))
