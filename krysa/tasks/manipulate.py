from . import Task, SortLayout
from functools import partial


class Manipulate(object):
    '''All :ref:`Task` s categorized as being able to `manipulate` data.
    A result after manipulation is a new data.
    '''

    def manip_sort(*args):
        '''Opens a :mod:`tasks.Task` with a :mod:`tasks.AddressLayout` that
        gets from user :ref:`Data` address.
        '''
        widget = SortLayout()
        task = Task(title='Sort', wdg=widget,
                    call=['Sort', Manipulate.manip_sort])
        task.run = partial(Manipulate._manip_sort,
                           task,
                           task.ids.container.children[0].ids.sort_type.text)
        task.open()

    @staticmethod
    def _manip_sort(task, sort_type, *args):
        '''Gets the values from address and returns the count.
        '''
        values = task.from_address(task.tablenum, ':all')
        task.set_page('Sort', str(len(values)), 'text')
        return
        # data here:
        rows = task.app.root._extract_rows(table[1].rv.data)[max_cols:]

        cnks = []
        for x in xrange(0, len(rows), max_cols):
            cnks.append(rows[x:x + max_cols])
        for chunk in cnks:
            _chunk = []
            for cnk in chunk:
                if not isinstance(cnk, (str, unicode)):
                    _chunk.append(unicode(cnk))
                else:
                    _chunk.append('\'' + cnk + '\'')
            values = ','.join(_chunk)
            c.execute(
                "INSERT INTO " + table[0] +
                " VALUES(" + values + ")"
            )

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
