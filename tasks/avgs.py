from tasks import Task, CountLayout
from functools import partial


def avgs_gen(self, *args):
    pass


def avgs_inter(self, *args):
    pass


def avgs_mid(self, *args):
    pass


def avgs_trim(self, *args):
    pass


def avgs_median(self, *args):
    pass


def avgs_mode(self, *args):
    pass


names = (('Generalized', avgs_gen),  # do conditions acc to P
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
