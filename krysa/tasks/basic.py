from . import Task, CountLayout, SmallLargeLayout, FreqLayout
from scipy.stats import relfreq, cumfreq
from functools import partial
import math


def basic_count(*args):
    widget = CountLayout()
    task = Task(title='Count', wdg=widget,
                call=['Count', basic_count])
    task.run = partial(_basic_count,
                       task,
                       task.ids.container.children[0].ids.name)
    task.open()


def _basic_count(task, address, *args):
    values = task.from_address(task.tablenum, address.text)
    task.set_page('Count', str(len(values)), 'text')


def basic_countifs(self, *args):
    pass


def basic_min(*args):
    widget = CountLayout()
    task = Task(title='Minimum', wdg=widget,
                call=['Minimum', basic_min])
    task.run = partial(_basic_min,
                       task,
                       task.ids.container.children[0].ids.name)
    task.open()


def _basic_min(task, address, *args):
    values = task.from_address(task.tablenum, address.text)
    task.set_page('Minimum', str(min(values)), 'text')


def basic_max(*args):
    widget = CountLayout()
    task = Task(title='Maximum', wdg=widget,
                call=['Maximum', basic_max])
    task.run = partial(_basic_max,
                       task,
                       task.ids.container.children[0].ids.name)
    task.open()


def _basic_max(task, address, *args):
    values = task.from_address(task.tablenum, address.text)
    task.set_page('Maximum', str(max(values)), 'text')


def basic_small(*args):
    widget = SmallLargeLayout()
    task = Task(title='Small', wdg=widget,
                call=['Small', basic_small])
    task.run = partial(_basic_small,
                       task,
                       task.ids.container.children[0].ids.name,
                       task.ids.container.children[0].ids.order)
    task.open()


def _basic_small(task, address, k, *args):
    values = task.from_address(task.tablenum, address.text)
    values = sorted(values)
    k = int(k.text) - 1
    try:
        task.set_page('Small ({}.)'.format(k + 1), str(values[k]), 'text')
    except IndexError:
        pass


def basic_large(self, *args):
    widget = SmallLargeLayout()
    task = Task(title='Large', wdg=widget,
                call=['Large', basic_large])
    task.run = partial(_basic_large,
                       task,
                       task.ids.container.children[0].ids.name,
                       task.ids.container.children[0].ids.order)
    task.open()


def _basic_large(task, address, k, *args):
    values = task.from_address(task.tablenum, address.text)
    values = sorted(values, reverse=True)
    k = int(k.text) - 1
    try:
        task.set_page('Large ({}.)'.format(k + 1), str(values[k]), 'text')
    except IndexError:
        pass  # throw error k out of len(values) bounds, same for *_small


def basic_freq(self, *args):
    # without intervals for now
    widget = FreqLayout()
    task = Task(title='Frequency', wdg=widget,
                call=['Frequency', basic_freq])
    task.run = partial(_basic_freq,
                       task,
                       task.ids.container.children[0].ids.name,
                       task.ids.container.children[0].ids.bins,
                       task.ids.container.children[0].ids.bins_auto,
                       task.ids.container.children[0].ids.lowlimit,
                       task.ids.container.children[0].ids.uplimit,
                       task.ids.container.children[0].ids.limits_auto,
                       task.ids.container.children[0].ids.absolute,
                       task.ids.container.children[0].ids.relative,
                       task.ids.container.children[0].ids.cumulative,
                       task.ids.container.children[0].ids.intervals)
    task.open()


def _basic_freq(task, address, bins, bins_auto, lowlimit, uplimit, limits_auto,
                absolute, relative, cumulative, intervals, *args):
    values = task.from_address(task.tablenum, address.text)
    values = [float(val) for val in values]
    values = sorted(values)
    cols = 1

    if limits_auto.active:
        lowlimit = min(values)
        uplimit = max(values)
    else:
        lowlimit = float(lowlimit.text)
        uplimit = float(uplimit.text)

    # get correct bins if no input
    if bins_auto.active:
        bins = uplimit + 1
    else:
        bins = int(bins.text)

    relat = []
    if relative.active:
        relat = relfreq(values, numbins=bins,
                        defaultreallimits=(lowlimit, uplimit))

        # something better than filter?
        relat = [float(val) for val in relat[0]]
        relat = filter(None, relat)
        relat.insert(0, 'Relative')
        cols += 1

    cumul = []
    if cumulative.active:
        cumul = cumfreq(values, numbins=bins,
                        defaultreallimits=(lowlimit, uplimit))
        cumul = [float(val) for val in cumul[0]]
        cumul = sorted(list(set(cumul)))
        cumul.insert(0, 'Cumulative')
        cols += 1

    absol = []
    if absolute.active:
        absol.append('Absolute')
        if intervals.active:
            if bins_auto.active:
                absol_bins = math.ceil(math.sqrt(len(values)))
            else:
                absol_bins = bins
            bin_size = float(uplimit - lowlimit) / float(absol_bins - 1)
            clean = [(lowlimit + bin_size * i) for i in xrange(bins)]

        else:
            clean = []
            for val in values:
                if val not in clean:
                    clean.append(val)

            for item in clean:
                absol.append(values.count(item))

        for i, c in enumerate(cumul[1:]):
            if i == 0 or i == len(cumul[1:]):
                absol.append(c)
            else:
                absol.append(c - cumul[1:][i - 1])
        cols += 1

    res = []
    clean.insert(0, 'Value')

    if absol and not relat and not cumul:
        res = [r for items in zip(clean, absol) for r in items]
    elif absol and relat and not cumul:
        res = [r for items in zip(clean, absol, relat) for r in items]
    elif absol and cumul and not relat:
        res = [r for items in zip(clean, absol, cumul) for r in items]
    elif relat and not absol and not cumul:
        res = [r for items in zip(clean, relat) for r in items]
    elif relat and cumul and not absol:
        res = [r for items in zip(clean, relat, cumul) for r in items]
    elif cumul and not absol and not relat:
        res = [r for items in zip(clean, cumul) for r in items]
    elif absol and relat and cumul:
        res = [r for items in zip(clean, absol, relat, cumul) for r in items]

    task.set_page('Frequency', res, 'table{}'.format(cols))


names = (('Count', basic_count),
         ('_Count ifs', basic_countifs),
         ('Minimum', basic_min),
         ('Maximum', basic_max),
         ('Small', basic_small),
         ('Large', basic_large),
         ('Frequency', basic_freq))
