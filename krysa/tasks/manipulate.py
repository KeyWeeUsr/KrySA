from kivy.uix.tabbedpanel import TabbedPanelItem
from . import Task, SortLayout
from functools import partial


class Manipulate(object):
    '''All :ref:`Task` s categorized as being able to `manipulate` data.
    A result after manipulation is a new data.
    '''

    def manip_sort(*args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.AddressLayout` that
        gets from user :ref:`data` address.
        '''
        widget = SortLayout()
        task = Task(title='Sort', wdg=widget,
                    call=['Sort', Manipulate.manip_sort])
        task.tablecls = task.app.tablecls
        task.run = partial(Manipulate._manip_sort,
                           task,
                           task.ids.container.children[0].ids.sort_type)
        task.open()

    @staticmethod
    def _manip_sort(task, sort_type, *args):
        '''Gets the values from address, sorts each column either ascending
        or descending and returns a new :mod:`main.Table`
        '''
        sort_type = 'Asc' not in sort_type.text
        from_address = task.from_address(task.tablenum, ':all', extended=True)
        values, cols, rows, labels = from_address

        # get separated cols to sort
        chunks = []
        for x in xrange(0, len(values), rows):
            chunks.append(values[x:x + rows])

        values = []
        for val in chunks:
            values.append(sorted(val, reverse=sort_type))

        # add Table
        table = task.ids.tablesel.text
        table += ' (desc)' if sort_type else ' (asc)'
        tabletab = TabbedPanelItem(text=table)
        task.app.root.ids.tabpanel.add_widget(tabletab)

        values = zip(*values)
        values = [v for vals in values for v in vals]
        task.app.root.tables.append((
            table, task.tablecls(max_cols=cols, max_rows=rows,
                                 pos=task.app.root.pos,
                                 size=task.app.root.size,
                                 values=values, labels=labels)
        ))
        tabletab.content = task.app.root.tables[-1][1]

    def manip_filter(*args):
        '''(Not yet implemented)
        '''

    def manip_append(*args):
        '''(Not yet implemented)
        '''

    def manip_split(*args):
        '''(Not yet implemented)
        '''

    def manip_merge(*args):
        '''(Not yet implemented)
        '''

    names = (('Sort', manip_sort),
             ('_Filter', manip_filter),
             ('_Append', manip_append),  # append (table, column, rows)
             ('_Split', manip_split),   # split into two data(columns, rows)
             ('_Merge', manip_merge))
