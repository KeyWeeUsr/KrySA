from . import Task, CountLayout, SmallLargeLayout
from functools import partial


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


def basic_countifs(self, *args): pass


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
        task.set_page('Small (%s.)' % (k + 1), str(values[k]), 'text')
    except:
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
        task.set_page('Large (%s.)' % (k + 1), str(values[k]), 'text')
    except:
        pass  # throw error k out of len(values) bounds, same for *_small


def basic_freq(self, *args): pass


names = (('Count', basic_count),
         ('_Count ifs', basic_countifs),
         ('Minimum', basic_min),
         ('Maximum', basic_max),
         ('Small', basic_small),
         ('Large', basic_large),
         ('_Frequency', basic_freq))
