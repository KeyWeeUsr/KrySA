from . import Task, SortLayout, AppendLayout, StandLayout
from kivy.uix.tabbedpanel import TabbedPanelItem
from functools import partial

# Py3 fixes
import sys
if sys.version_info[0] >= 3:
    unicode = str
    str = bytes
    xrange = range


class Manipulate(object):
    '''All :ref:`Task` s categorized as being able to `manipulate` data.
    A result after manipulation is a new data.

    .. versionadded:: 0.3.5
    '''

    def manip_sort(*args):
        '''Open a :mod:`tasks.Task` with a :mod:`tasks.SortLayout` that gets
        from user the table which will be sorted and the type of sorting
        (`Ascending` or `Descending`). Create a new :mod:`main.Table`.

        .. versionadded:: 0.3.5
        '''
        widget = SortLayout()
        task = Task(title='Sort', wdg=widget,
                    call=['Sort', Manipulate.manip_sort])
        task.tablecls = task.app.tablecls
        container = task.ids.container.children[0]
        task.run = partial(Manipulate._manip_sort,
                           task,
                           container.ids.sort_type)
        task.open()

    @staticmethod
    def _manip_sort(task, sort_type, *args):
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
        '''Open a :mod:`tasks.Task` with a :mod:`tasks.AppendLayout` that gets
        from user :mod:`main.Table`, type of append and an amount of empty
        rows / cols to append.

        The function either returns a new, altered :mod:`main.Table` of
        selected one, or appends directly to the selected :class:`main.Table`.

        .. versionadded:: 0.3.6
        .. versionchanged:: 0.3.7
            Added overwriting of selected :mod:`main.Table`
        .. versionchanged:: 0.5.5
            Added append for new columns
        '''
        widget = AppendLayout()
        task = Task(title='Append', wdg=widget,
                    call=['Append', Manipulate.manip_append])
        task.tablecls = task.app.tablecls
        container = task.ids.container.children[0]
        task.run = partial(Manipulate._manip_append,
                           task,
                           container.ids.what,
                           container.ids.amount,
                           container.ids.cols_container,
                           container.ids.overwrite)
        task.open()

    @staticmethod
    def _manip_append(task, append_type, amount, container, overwrite, *args):
        append_type = append_type.text
        overwrite = overwrite.active
        amount = int(amount.text) if amount.text else 0

        if append_type == 'Append type':
            raise Exception('No append type was chosen!')

        # Stop the task if no amount (or =0) is specified
        # or if no column is available
        if not amount and not container.children:
            raise Exception('No amount was specified!')

        from_address = task.from_address(task.tablenum, ':all',
                                         extended=True)
        values, cols, rows, labels = from_address
        rows = int(rows)

        # get columns
        chunks = []
        for x in xrange(0, len(values), rows):
            chunks.append(values[x:x + rows])
        if append_type == 'Columns':
            _cols = container.children[0].ids.columns.children
            for c in reversed(_cols):
                labels.append(c.ids.colname.text)
                _type = c.ids.coltype.text
                if _type == 'INTEGER':
                    chunks.extend([[0 for _ in range(rows)]])
                elif _type == 'REAL':
                    chunks.extend([[0.0 for _ in range(rows)]])
                else:
                    chunks.extend([[u'' for _ in range(rows)]])
                amount += 1
                cols += 1

        elif append_type == 'Rows':
            # append to columns a zero value according
            # to their type int(amount)-times
            for r in range(amount):
                for chunk in chunks:
                    if isinstance(chunk[0], int):
                        chunk.append(0)
                    elif isinstance(chunk[0], float):
                        chunk.append(0.0)
                    else:
                        chunk.append(u'')

            # increase row count by new rows
            rows += amount

        # zip chunks to values, flatten values
        values = zip(*chunks)
        values = [v for vals in values for v in vals]

        # add Table
        tab_pos = 0
        table = task.ids.tablesel.text
        tabpanel = task.app.root.ids.tabpanel
        tabpanel_len = len(tabpanel.tab_list)
        if overwrite:
            tab_pos = task.tablenum
            # list of available tabs in Task is 0 -> n (from tables),
            # but tab_list order is reversed in Kivy, therefore
            # reverse the index by going backwards with -1
            # and increase tab_pos, which is only index of
            # value order in spinner
            old_tab = tabpanel.tab_list[-1 - (tab_pos + 1)]
            tabpanel.remove_widget(old_tab)
            tabletab = TabbedPanelItem(text=table)
            tabpanel.add_widget(tabletab, tabpanel_len - 1 - (tab_pos + 1))
        else:
            # if space in name, sql save boom
            if append_type == 'Columns':
                table += u'_append_{}_cols'.format(unicode(amount))
            elif append_type == 'Rows':
                table += u'_append_{}_rows'.format(unicode(amount))
            tabletab = TabbedPanelItem(text=table)
            tabpanel.add_widget(tabletab, 0)

        # make new table
        new_table = (
            table, task.tablecls(max_cols=cols, max_rows=rows,
                                 pos=task.app.root.pos,
                                 size=task.app.root.size,
                                 values=values, labels=labels)
        )

        # place newly created table into tab's content
        if overwrite:
            task.app.root.tables[tab_pos] = new_table
            tabletab.content = task.app.root.tables[tab_pos][1]
        else:
            task.app.root.tables.append(new_table)
            tabletab.content = task.app.root.tables[-1][1]

    def manip_split(*args):
        '''(Not yet implemented)
        '''

    def manip_merge(*args):
        '''(Not yet implemented)
        '''

    def manip_stand(*args):
        '''(Not yet implemented)
        Standardizing specified columns from data according to various
        types of standardiztion.
        '''
        widget = StandLayout()
        task = Task(title='Standardize', wdg=widget,
                    call=['Standardize', Manipulate.manip_stand])
        task.tablecls = task.app.tablecls
        container = task.ids.container.children[0]
        task.run = partial(Manipulate._manip_stand,
                           task)
        task.open()

    @staticmethod
    def _manip_stand(task, *args):
        pass

    names = (('Sort', manip_sort),
             ('_Filter', manip_filter),
             ('Append', manip_append),
             ('_Split', manip_split),   # split into two data(columns, rows)
             ('_Merge', manip_merge),
             ('_Standardize', manip_stand))
