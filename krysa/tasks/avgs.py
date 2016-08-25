from . import Task, AvgsLayout
from functools import partial, reduce
import operator
import math


class Avgs(object):
    """All :ref:`Task` s categorized as `averages` under one roof.
    """

    def avgs_gen(*args):
        """Generalized mean:

        .. math::
           \\big(\\frac{1}{n}\\sum_{i=1}^n  x_{i}^{p} \\big)^\\frac{1}{p},
           where:

        * p == -1: harmonic
        * p == 0: geometric
        * p == 1: arithmetic
        * p == 2: quadratic
        * p == 3: cubic
        * etc...
        """
        widget = AvgsLayout()
        task = Task(title='Count', wdg=widget,
                    call=['Count', Avgs.avgs_gen])
        task.run = partial(Avgs._avgs_gen,
                           task,
                           task.ids.container.children[0].ids.name,
                           task.ids.container.children[0].ids.power)
        task.open()

    @staticmethod
    def _avgs_gen(task, address, p, *args):
        """Gets the values from address and depending on `p` (power) value
        returns either exceptional case for `p == 0` (geometric mean), or
        value from the generalized mean's formula.
        """
        try:
            if p == '-0':
                p = 0.0
            else:
                p = float(p.text)
        except ValueError, SyntaxError:
            return
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
        """(Not yet implemented)
        """

    def avgs_mid(*args):
        """(Not yet implemented)
        """

    def avgs_trim(*args):
        """(Not yet implemented)
        """

    def avgs_median(*args):
        """(Not yet implemented)
        """

    def avgs_mode(*args):
        """(Not yet implemented)
        """

    names = (('Generalized', avgs_gen),
             ('Interquartile', avgs_inter),
             ('Midrange', avgs_mid),
             ('Trimmed', avgs_trim),
             ('Median', avgs_median),
             ('Mode', avgs_mode))

    # statistics.mean()
    # numpy.mean(values)
    # scipy.stats.gmean(values)
    # scipy.stats.hmean(values)
    # 1/2 * ( max(x) + min(x) )
    # scipy.stats.tmean(values, limits)
