from . import Task, CountLayout, AvgsLayout
from functools import partial, reduce
import operator
import math


def avgs_gen(*args):
    '''Generalized mean:

    .. math::
       \\big(\\frac{1}{n}\\sum_{i=1}^n  x_{i}^{p} \\big)^\\frac{1}{p}, where:

    * p == -1: harmonic
    * p == 0: geometric
    * p == 1: arithmetic
    * p == 2: quadratic
    * p == 3: cubic
    * etc...
    '''
    widget = AvgsLayout()
    task = Task(title='Count', wdg=widget,
                call=['Count', avgs_gen])
    task.run = partial(_avgs_gen,
                       task,
                       task.ids.container.children[0].ids.name,
                       task.ids.container.children[0].ids.power)
    task.open()


def _avgs_gen(task, address, p, *args):
    try:
        p = float(p.text)
    except ValueError, SyntaxError:
        return
    values = task.from_address(task.tablenum, address.text)
    if p == 0:
        multiples = reduce(operator.mul, values, 1)
        result = math.pow(multiples, 1/float(len(values)))
        p = 'geometric'
    else:
        values = [math.pow(val, p) for val in values]
        result = math.pow(math.fsum(values)/float(len(values)), 1/float(p))
    task.set_page('Generalized mean({})'.format(p), str(result), 'text')


def avgs_inter(*args):
    pass


def avgs_mid(*args):
    pass


def avgs_trim(*args):
    pass


def avgs_median(*args):
    pass


def avgs_mode(*args):
    pass


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
