# -*- coding: utf-8 -*-
# KrySA - Statistical analysis for rats
# Version: 0.4.0
# Copyright (C) 2016, KeyWeeUsr(Peter Badida) <keyweeusr@gmail.com>
# License: GNU GPL v3.0, More info in LICENSE.txt

from kivy.config import Config
import os

# local & RTD docs fix
if not any(['BUILDDIR' in os.environ, 'READTHEDOCS' in os.environ]):
    Config.set('graphics', 'window_state', 'maximized')
    import numpy
    import scipy

import re
import json
import math
import string
import sqlite3
import os.path as op
from kivy.app import App
from kivy.clock import Clock
from functools import partial
from dropdown import DropDown
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.label import Label
from time import gmtime, strftime
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.properties import StringProperty, ObjectProperty, \
    BooleanProperty, ListProperty

from tasks import Task
from tasks.basic import Basic
from tasks.avgs import Avgs
from tasks.manipulate import Manipulate


class ResultGrid(GridLayout):
    '''A black gridlayout, together with :mod:`main.Wrap` makes a table
    container for results that need a table.

    .. versionadded:: 0.3.2
    '''


class Wrap(Label):
    '''A white label with automatically wrapped text.

    .. versionadded:: 0.3.2
    '''
    background_color = ListProperty([0, 0, 0, 0])


class PageBox(BoxLayout):
    '''A layout that includes Page widget together with transparent separator.
    It's used for adding new results from Tasks.

    .. versionadded:: 0.2.0
    '''
    def __init__(self, **kwargs):
        super(PageBox, self).__init__(**kwargs)
        self.add_widget = self.ids.page.add_widget


class PaperLabel(Label):
    '''A label with visual properties as a paper sheet.

    .. versionadded:: 0.2.0
    '''


class ImgButton(Button):
    '''A button with an image of square shape in the middle.

    .. versionadded:: 0.2.0
    '''
    source = StringProperty('')


class ErrorPop(Popup):
    '''An error popup to let user know something is missing or typed wrong
    when console is disabled.

    .. versionadded:: 0.1.2
    '''
    message = StringProperty('')

    def __init__(self, **kw):
        self.message = kw.get('msg', '')
        super(ErrorPop, self).__init__(**kw)


class NewDataValue(BoxLayout):
    '''A layout handling the behavior of inputs and button for each new
    value in :ref:`data`.

    .. versionadded:: 0.1.4
    '''
    def __init__(self, **kw):
        self.app = App.get_running_app()
        super(NewDataValue, self).__init__(**kw)
        self.filter = kw['filter']


class NewDataColumn(BoxLayout):
    '''A layout handling the behavior of type, values(``NewDataValue``) and
    some buttons for each new column in :ref:`data`.

    .. versionadded:: 0.1.4
    '''
    def __init__(self, **kw):
        self.app = App.get_running_app()
        super(NewDataColumn, self).__init__(**kw)

    @staticmethod
    def free(items):
        '''Frees all locked cells in the column except a column type. If
        a wrong type is used, removing the whole column is necessary.
        (protection against corrupting :ref:`sqlite`)

        .. versionadded:: 0.1.4
        '''
        for item in items:
            if hasattr(item, 'disabled'):
                try:
                    if item.parent.ids['coltype'] == item:
                        continue
                except:
                    item.disabled = False
            else:
                # enable children
                for i in item:
                    try:
                        if i.parent.ids['coltype'] == item:
                            continue
                    except:
                        i.disabled = False

    def checklock(self, disable, coltype, check, *args):
        '''Disables all cells in the column, then check them against a list
        of strings that could be used to corrupt :ref:`sqlite` . If the check
        is done without an error, another check is made to protect against
        using an empty string ``''`` as a value, which if used inappropriately
        results in a crash.

        .. versionadded:: 0.1.4
        '''
        msg = 'Please remove any SQL keyword present in the column!'

        for item in disable:
            if hasattr(item, 'disabled'):
                item.disabled = True
            else:
                # disable children
                for i in item:
                    i.disabled = True

        # check for any sql keywords and correct values
        for item in check:
            try:
                for keyword in self.app.sql_blacklist:
                    if keyword in item.text.upper():
                        error = ErrorPop(msg=msg)
                        error.open()
                        return
            except AttributeError:
                for i in item.children:
                    for keyword in self.app.sql_blacklist:
                        if keyword in i.ids.value.text.upper():
                            error = ErrorPop(msg=msg)
                            error.open()
                            return
                    try:
                        if not coltype.text == 'TEXT':
                            float(i.ids.value.text)
                    except ValueError:
                        if coltype.text == 'REAL':
                            i.ids.value.text = '0.0'
                        elif coltype.text == 'INTEGER':
                            i.ids.value.text = '0'

    def paste(self, values, sep):
        '''Paste a value(s) from a user's clipboard as a column values. A user
        can choose what kind of separator was used on the values, for example::

            1 2 3 4 5     # (space)
            1\\t2\\t3\\t4\\t  # (tab)
            1\\n2\\n3\\n4\\n  # Unix-like new line character (<enter>/<return>)

        If in doubt and your values were copied from a column (e.g.
        spreadsheet), use `OS default`, which will choose between ``\\n``
        (Unix-like) or ``\\r\\n`` (Windows) new line separators.

        .. versionadded:: 0.3.4
        '''
        if sep == 'space':
            values = values.split(' ')
        elif sep == 'OS default':
            values = values.split(os.linesep)
        else:
            values = values.split(sep[1:])
        for val in values:
            v = NewDataValue(filter=self.filter)
            v.ids.value.text = val
            self.ids.vals.add_widget(v)
        self.ids.vals.parent.scroll_to(self.ids.vals.children[0])


class NewDataLayout(BoxLayout):
    '''A layout handling the behavior of ``NewDataColumn`` and some inputs for
    each new value in :ref:`data`.

    .. versionadded:: 0.1.3
    '''
    def __init__(self, **kw):
        self.app = App.get_running_app()
        super(NewDataLayout, self).__init__(**kw)


class CreateWizard(Popup):
    '''A popup handling the behavior for creating a new :ref:`data`,
    i.e a wizard.

    .. versionadded:: 0.1.3
    '''
    run = ObjectProperty(None)

    def __init__(self, **kw):
        super(CreateWizard, self).__init__(**kw)
        self.run = kw.get('run')
        wdg = kw.get('wdg')
        if wdg:
            self.ids.container.add_widget(wdg)


class Dialog(Popup):
    '''A dialog handling the behavior for creating or opening files e.g.
    :ref:`project` or :ref:`data`.

    .. versionadded:: 0.1.0
    '''
    confirm = StringProperty('')
    run = ObjectProperty(None)
    dirs = BooleanProperty(False)
    project = BooleanProperty(False)
    filter = ListProperty([])

    def __init__(self, **kw):
        super(Dialog, self).__init__(**kw)
        self.confirm = kw.get('confirm', '')
        self.run = kw.get('run')
        self.dirs = kw.get('dirs', False)
        self.project = kw.get('project', False)
        if self.project:
            self.ids.name.hint_text = 'Project.krysa'
            self.filter = [lambda folder, fname: fname.endswith('.krysa')]
        else:
            self.ids.name.hint_text = 'example.sqlite'
            self.filter = [lambda folder, fname: fname.endswith('.sqlite')]


class SideItem(BoxLayout):
    '''Supposed to be a part of settings, most likely will be removed/replaced.

    .. versionadded:: 0.1.0
    '''


class TableItem(TextInput):
    '''An item handling the behavior or each separate value in the
    :mod:`main.Table` such as updating/editing values in :ref:`data`.

    .. versionadded:: 0.1.0
    '''
    def __init__(self, **kwargs):
        super(TableItem, self).__init__(**kwargs)
        self.bind(focus=self.on_focus)

    def on_focus(self, widget, focused):
        '''Makes sure the unconfirmed value is discarded e.g. when clicked
        outside of the widget.
        '''
        if not focused:
            self.text = self.old_text

    def update_value(self, txt, *args):
        '''On ``<enter>`` (``return``) key updates the values
        :mod:`main.TableItem.text` and :mod:`main.TableItem.old_text` in
        :mod:`main.Table`.

        .. versionadded:: 0.1.0
        '''
        data = []
        cols = self.cols - 1

        for i in self.origin.data:
            if 'cell' in i:
                data.append(i)
        chunks = [data[x:x + cols] for x in xrange(0, len(data), cols)]

        orig_type = type(chunks[self.r][self.c - 1])
        place = self.cols * (self.r + 1) - (self.cols - self.c)
        self.origin.data[place]['text'] = txt
        self.origin.data[place]['old_text'] = txt
        self.origin.refresh_from_data()


class Table(ScrollView):
    '''A view handling the behavior of the inputs from :ref:`sqlite`. Separates
    the values from :ref:`sqlite` according to its :ref:`data`'s column types
    into three Python categories - `int`, `float` or `unicode` and assigns
    an alphabetic order for each column together with row number to each value.

    .. versionadded:: 0.1.0
    '''
    # use with ....add_widget(Table(max_cols=3, max_rows=3))
    # Grid -> Scroll, grid as container - better for sizing and placing

    # set "address" for table pos in grid to item
    number_size = (30, 30)
    default_size = (100, 30)

    def __init__(self, **kw):
        app = App.get_running_app()
        self.rv = RecycleView(bar_width='10dp',
                              scroll_type=['bars', 'content'])
        container = RecycleGridLayout(size_hint=(None, None))
        container.viewclass = TableItem
        container.bind(minimum_size=container.setter('size'))

        self.max_rows = kw.get('max_rows', 1)
        self.rows = self.max_rows + 1
        self.max_cols = kw.get('max_cols', 1)
        self.cols = self.max_cols + 1
        self.values = kw.get('values', [])
        self.labels = kw.get('labels')
        self.types = kw.get('types')

        container.rows = self.rows
        container.cols = self.cols

        ltr = [' (' + letter + ')' for letter in self.get_letters()]
        self.rv.add_widget(container)

        if 'item_size' not in kw:
            item_size = self.default_size
        super(Table, self).__init__(**kw)
        for r in range(self.rows):
            for c in range(self.cols):
                if r == 0:
                    if c == 0:
                        self.rv.data.append({'text': u'', 'disabled': True,
                                             'size': self.number_size,
                                             'origin': self.rv})
                    else:
                        self.rv.data.append(
                            {
                                'text': self.labels[c - 1] + ltr[c - 1],
                                '_text': self.labels[c - 1],
                                'disabled': True,
                                'cell': 'label' + str(c - 1),
                                'type': type(u''),
                                'size': self.default_size,
                                'origin': self.rv
                            }
                        )
                else:
                    if c == 0:
                        self.rv.data.append({'text': unicode(r),
                                             'disabled': True,
                                             'size': self.number_size,
                                             'origin': self.rv})
                    else:
                        filter = app.root.simple_chars
                        try:
                            val = self.values.pop(0)
                            text_type = type(val)
                            filter_val = repr(text_type)[7:-2]
                            if filter_val in ['int', 'float']:
                                filter = filter_val
                        except IndexError:
                            print 'values < space'
                            val = '.'

                        if 'e+' in str(val) or 'e-' in str(val):
                            val = '{0:.10f}'.format(val)
                        if self.types:
                            if self.types[c - 1] == 'INTEGER':
                                filter = 'int'
                                text_type = type(1)
                            elif self.types[c - 1] == 'REAL':
                                filter = 'float'
                                text_type = type(1.1)
                        self.rv.data.append(
                            {
                                'text': unicode(val),
                                'old_text': unicode(val),
                                'disabled': False,
                                'cell': self.labels[c - 1] + str(r),
                                'r': r,
                                'rows': self.rows,
                                'c': c,
                                'cols': self.cols,
                                'type': text_type,
                                'size': self.default_size,
                                'input_filter': filter,
                                'origin': self.rv
                            }
                        )
        if self.values:
            raise Exception('Not enough space for all values! \
                            Increase rows/cols!')
        self.add_widget(self.rv)

    def get_letters(self):
        '''Gets a list of letters the same length as :ref:`data`'s columns.

        .. versionadded:: 0.1.0
        '''
        letters = [chr(letter + 65) for letter in range(26)]
        result = []
        label = []
        cols = range(self.cols + 1)
        for i in cols:
            if i != 0:
                while i:
                    i, rem = divmod(i - 1, 26)
                    label[:0] = letters[rem]
                result.append(''.join(label))
                label = []
        return result

    def lock(self, disabled=True):
        '''docs

        .. versionadded:: 0.1.0
        '''
        for i in self.rv.data:
            if 'cell' in i and 'label' not in i['cell']:
                i['disabled'] = disabled
        self.rv.refresh_from_data()

    def clean(self, *args):
        '''Removes all data from :mod:`main.Table`

        .. versionadded:: 0.1.0
        '''
        self.rv.data = []


class ProcessFlow(BoxLayout, StencilView):
    '''A canvas on which will be displayed actions for each :ref:`data` related
    to them, such as used tasks connected with result of the tasks.

    .. versionadded:: 0.1.0

    (Not implemented yet)
    '''
    def __init__(self, **kw):
        super(ProcessFlow, self).__init__(**kw)
        app = App.get_running_app()
        self.texture = Image(source=app.path + '/data/grid.png').texture
        self.texture.wrap = 'repeat'


class SizedButton(Button):
    '''A button with width automatically customized according to text length of
    its siblings, which makes every sibling the same size as the one with the
    longest text string.

    .. versionadded:: 0.1.0
    '''
    def correct_width(self, *args):
        self.width = self.texture_size[0] + 8
        self.parent.parent.width = max([c.width for c in self.parent.children])
        for child in self.parent.children:
            child.width = self.parent.parent.width


class MenuDrop(DropDown):
    '''A list of :mod:`main.SizedButton` s displayed as a menu, where each
    button may create another menu depending on the function bound to it. The
    main menu is handled through a single instance of :mod:`main.MenuDrop`
    which is instantiated before :mod:`main.Krysa.build` function.

    Each click/tap on the menu button then assigns a value to it from
    ``App.menu`` dictionary according to its name in `kv` file.

    .. versionadded:: 0.1.0
    '''
    def __init__(self, **kw):
        app = App.get_running_app()
        app.drop = self
        super(MenuDrop, self).__init__(**kw)

    def click(self, instance, values):
        for value in values:
            btn = SizedButton(text=value[0])
            btn.bind(on_release=value[1])
            self.add_widget(btn)
        self.open(instance)

    def on_dismiss(self, *args):
        self.clear_widgets()


class Body(FloatLayout):
    '''The main layout for the application. It handles menu values, their
    appropriate functions, filtering of user's input and functions for
    accessing :ref:`sqlite` in :mod:`main.Table`.

    .. versionadded:: 0.1.0
    '''
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.tables = []
        self.app.menu = {'file': (['New...', self.new],
                                  ['Open Project', self.open_project],
                                  ['Close Project', self.close_project],
                                  ['Save Project', self.save_project],
                                  ['Import Data', self.import_data],
                                  ['Export Data', self.export_data],
                                  ['_Recent Projects', self.test],
                                  ['Exit', self.app.stop],),
                         'edit': (['_Undo', self.test],
                                  ['_Redo', self.test],
                                  ['_Cut', self.test],
                                  ['_Copy', self.test],
                                  ['_Paste', self.test],
                                  ['_Delete', self.test],
                                  ['_Find...', self.test],
                                  ['_Replace...', self.test],
                                  ['_Protect Data', self.test],
                                  ['_Go To...', self.test],),
                         'tasks': (['Basic', self.basic],
                                   ['Averages', self.avgs],
                                   ['Manipulate', self.manipulate],),
                         'help': (['_KrySA Help', self.test],
                                  ['_Getting Started Tutorial', self.test],
                                  ['About KrySA', self.about],),
                         }
        super(Body, self).__init__(**kw)

    def new(self, button, *args):
        '''Opens a submenu for ``New`` menu.

        .. versionadded:: 0.1.0
        '''
        d = DropDown(allow_sides=True, auto_width=False)
        buttons = []

        # Project saving works, but implementing ProcessFlow is still ToDo
        buttons.append(SizedButton(text='Project'))
        buttons[0].bind(on_release=self._new_project)
        buttons.append(SizedButton(text='Data'))
        buttons[1].bind(on_release=self._new_data)
        for b in buttons:
            d.add_widget(b)
        d.open(button)

    def _new_project(self, *args):
        '''Closes already opened :ref:`project` if available and opens a dialog
        for creating a new one.

        .. versionadded:: 0.1.2
        '''
        self.close_project()
        self.savedlg = Dialog(title='New Project',
                              confirm='Save',
                              run=self._save_project,
                              dirs=True,
                              project=True)
        self.savedlg.open()

    def _new_data(self, *args):
        '''Opens a wizard for creating a new :ref:`data` if a :ref:`project` is
        available or shows a warning if it doesn't exist.

        .. versionadded:: 0.1.3
        '''
        if not self.app.project_exists:
            error = ErrorPop(msg='No project exists!')
            error.open()
            return
        widget = NewDataLayout()
        self.wiz_newdata = CreateWizard(title='New Data', wdg=widget,
                                        run=partial(self._save_data, widget))
        self.wiz_newdata.open()

    def _save_data(self, wizard, *args):
        '''Gets data from the wizard, puts them into :mod:`main.Table` and exports them
        into :ref:`sqlite`.

        .. versionadded:: 0.1.4
        '''
        labels = []
        types = []
        values = []
        table_name = wizard.ids.table_name.text

        if not len(table_name):
            error = ErrorPop(msg='Please name your data!')
            error.open()
            return
        if not len(wizard.ids.columns.children):
            error = ErrorPop(msg='There must be at least one column!')
            error.open()
            return

        for child in reversed(wizard.ids.columns.children):
            child.ids.checklock.dispatch('on_release')
        for child in reversed(wizard.ids.columns.children):
            if child.ids.colname.text not in labels:
                lbl = re.findall(r'([a-zA-Z0-9])', child.ids.colname.text)
                if not len(lbl):
                    error = ErrorPop(msg='Use only a-z A-Z 0-9 characters!')
                    error.open()
                    return
                labels.append(''.join(lbl))
            else:
                error = ErrorPop(msg='Each column must have a unique name!')
                error.open()
                return

            types.append(child.ids.coltype.text)
            column_values = []

            for value_wdg in reversed(child.ids.vals.children):
                column_values.append(value_wdg.ids.value.text)
            values.append(column_values)

        max_cols = len(values)
        max_rows = len(max(values, key=len))

        # create table in KrySA, then export
        tabletab = TabbedPanelItem(text=table_name)
        self.ids.tabpanel.add_widget(tabletab)
        _values = values[:]
        values = []

        for i in range(max_rows):
            for j in range(max_cols):
                try:
                    values.append(_values[j][i])
                except IndexError:
                    if types[j] == 'INTEGER':
                        values.append(0)
                    elif types[j] == 'REAL':
                        values.append(0.0)
                    else:
                        values.append(u'')

        self.tables.append((table_name, Table(max_cols=max_cols,
                                              max_rows=max_rows, pos=self.pos,
                                              size=self.size, values=values,
                                              labels=labels, types=types)))
        tabletab.content = self.tables[-1][1]

        # export to data.sqlite in <project>/data directory
        data = op.join(self.app.project_dir, 'data')

        self._export_data([data], 'data.sqlite')
        self.wiz_newdata.dismiss()

    def open_project(self, *args):
        self.close_project()
        self.opendlg = Dialog(title='Open Project',
                              confirm='Open',
                              run=self._open_project,
                              project=True)
        self.opendlg.open()

    def _open_project(self, selection, *args):
        '''Opens a :ref:`project` from path selected in ``Dialog`` and imports
        :ref:`sqlite`.

        .. versionadded:: 0.1.7
        '''
        if not selection:
            return
        else:
            selection, fname = op.split(selection[0])

        data = op.join(selection, 'data')
        results = op.join(selection, 'results')

        self.app.project_exists = True
        self.app.project_dir = selection
        self.app.project_name = fname.split('.')[0]

        # (dummy for now)
        # dump widgets' properties from process flow to dict, then to json
        with open(op.join(selection, fname), 'rb') as f:
            project = json.loads(f.read())
        print project

        # import from project automatically
        self._import_data([op.join(data, 'data.sqlite')])

        # import results
        for file in os.listdir(results):
            self.set_page('', op.join(results, file), result_type='import')

    def close_project(self, *args):
        '''Clears all important variables, removes all :ref:`data` available in
        :mod:`main.Table` and switches to :mod:`main.ProcessFlow`.

        .. versionadded:: 0.1.0
        '''
        # call this before a new project
        self.app.project_exists = False
        self.app.project_dir = ''
        self.app.project_name = ''
        tp = self.ids.tabpanel
        while len(tp.tab_list) > 1:
            self.tables.pop()
            tp.remove_widget(tp.tab_list[0])
        self.ids.flow.clear_widgets()
        tp.switch_to(tp.tab_list[0])

    def save_project(self, *args):
        # same as _new_project + export data & results

        # make some output if unsaved changes available(e.g. * before name)
        if self.app.project_exists:
            self._save_project()
            return
        self.savedlg = Dialog(title='New Project',
                              confirm='Save',
                              run=self._save_project,
                              dirs=True,
                              project=True)
        self.savedlg.open()

    def _save_project(self, selection=None, fname=None, *args):
        '''Saves a :ref:`project` to path selected in ``Dialog`` and exports
        :ref:`sqlite`.

        .. versionadded:: 0.1.2
        '''
        if not selection:
            if not self.app.project_exists:
                return
            selection = op.dirname(self.app.project_dir)
            fname = self.app.project_name
        else:
            selection = selection[0]
        if '.' not in fname:
            fname = fname + '.krysa'

        if selection != op.dirname(self.app.project_dir):
            try:
                os.mkdir(op.join(selection, fname.split('.')[0]))
            except OSError:
                error = ErrorPop(msg='Project folder already exists!')
                error.open()
                return

        selection = op.join(selection, fname.split('.')[0])
        data = op.join(selection, 'data')
        results = op.join(selection, 'results')
        if selection != self.app.project_dir:
            os.mkdir(data)
            os.mkdir(results)
        if op.exists(op.join(selection, fname)):
            os.remove(op.join(selection, fname))

        self.app.project_exists = True
        self.app.project_dir = selection
        self.app.project_name = fname.split('.')[0]

        # (dummy for now)
        # dump widgets' properties from process flow to dict, then to json
        project = {u'test': u'blah'}
        with open(op.join(selection, fname), 'wb') as f:
            f.write(json.dumps(project, indent=4))

        # let user set table columns, add to tab, then:
        self._export_data([data], 'data.sqlite')

        # exporting results to pdf -> 0.3.x
        self._export_results(results)

    def import_data(self, *args):
        self.opendlg = Dialog(title='Import Data',
                              confirm='Import',
                              run=self._import_data)
        self.opendlg.open()

    def _import_data(self, selection, *args):
        '''Imports :ref:`sqlite` from path selected in ``Dialog`` and puts it
        to :mod:`main.Table`.

        .. versionadded:: 0.1.0
        '''
        # limit table name and column name to [a-zA-Z]

        # CREATE TABLE test(
        #                   Column INTEGER NOT NULL CHECK(
        #                               typeof(Column) = 'integer'))
        if not selection:
            return
        else:
            selection = selection[0]
            if '.sqlite' not in selection:
                return

        conn = sqlite3.connect(op.join(selection))
        c = conn.cursor()

        # get tables first!
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [tab[0] for tab in c.fetchall()]

        for table in tables:
            c.execute("pragma table_info({0})".format(table))
            table_info = c.fetchall()
            labels = [lbl[1] for lbl in table_info]

            # allow only: INTEGER, REAL, TEXT
            try:
                types = [type[2][0] for type in table_info]
            except IndexError:
                error = ErrorPop(msg='Bad file: No defined types in columns!')
                error.open()
                return

            tabletab = TabbedPanelItem(text=table)
            self.ids.tabpanel.add_widget(tabletab)
            c.execute('select * from {0}'.format(table))
            values = [item for item in c.fetchone()]
            max_cols = len(values)
            values += [item for sublist in c.fetchall() for item in sublist]
            max_rows = int(math.ceil(len(values) / float(max_cols)))
            self.tables.append((table, Table(max_cols=max_cols,
                                             max_rows=max_rows, pos=self.pos,
                                             size=self.size, values=values,
                                             labels=labels)))
            tabletab.content = self.tables[-1][1]
        self.opendlg.dismiss()
        conn.close()
        # ToDo: implement automatic saving to Project's data.sqlite
        # ToDo: if the same table name exist in tables, add ' (2)' or something

    def export_data(self, *args):
        self.savedlg = Dialog(title='Export Data',
                              confirm='Export',
                              run=self._export_data,
                              dirs=True)
        self.savedlg.open()

    @staticmethod
    def _extract_rows(data):
        '''Extract values from :mod:`main.Table`'s dictionary into a flat list.

        Example:

        ===== ===== =====
        Data1 Data2 Data3
          1    2.0    3
        ===== ===== =====

        [u'Data1', u'Data2', u'Data3', u'1', 2.0, 3, ...]

        .. versionadded:: 0.1.0
        '''
        rows = []
        for item in data:
            try:
                item['cell']
                if issubclass(item['type'], float):
                    rows.append(float(item['text']))
                elif issubclass(item['type'], int):
                    rows.append(int(item['text']))
                else:
                    rows.append(item['text'])
            except KeyError:
                pass

            # protect against '' values -> int(''), float('')
            except ValueError:
                # duplicated zeros to prevent sqlite3.IntegrityError
                # - raised when there is type checking for inserting
                # values to the table e.g. type(0) != type(0.0)
                if issubclass(item['type'], float):
                    rows.append(0.0)
                elif issubclass(item['type'], int):
                    rows.append(0)

        data = []
        return rows

    def _export_data(self, selection, fname, *args):
        '''Exports all available :ref:`data` (visible as tabs) as :ref:`sqlite`
        into path selected in ``Dialog``.

        .. versionadded:: 0.1.1
        '''
        col_types = {"<type 'int'>": 'INTEGER', "<type 'float'>": 'REAL'}
        if not selection:
            return
        else:
            selection = selection[0]
        if op.exists(op.join(selection, fname)):
            os.remove(op.join(selection, fname))

        conn = sqlite3.connect(op.join(selection, fname))
        c = conn.cursor()

        for table in self.tables:
            col_string = ''
            max_cols = table[1].max_cols
            columns = table[1].rv.data[1:max_cols + 1]  # types need whole dict
            types = table[1].rv.data[max_cols + 2:2 * (max_cols + 1)]

            for i, col in enumerate(columns):
                try:
                    type = col_types[repr(types[i]['type'])]
                except KeyError:
                    type = 'TEXT'
                # force column to check inserted values
                col_string += (
                    col['_text'] + " " + type +
                    " NOT NULL CHECK(typeof(" + col['_text'] +
                    ") = '" + type.lower() + "'),"
                )

            if col_string.endswith(','):
                col_string = col_string[:-1]
            c.execute(
                "CREATE TABLE " + table[0] + "(" + col_string + ")"
            )
            rows = self._extract_rows(table[1].rv.data)[max_cols:]

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
            conn.commit()
        conn.close()

        try:
            self.savedlg.dismiss()
        except AttributeError:
            # either closed, or wasn't even opened
            pass

    def _export_results(self, selection, *args):
        if not selection:
            return
        for file in os.listdir(selection):
            os.remove(op.join(selection, file))
        result_wdg = self.ids.results
        for i, result in enumerate(reversed(self.ids.results.children)):
            try:
                where = op.join(selection, str(i).zfill(3) + '.png')
                result.children[2].children[0].export_to_png(where)
            except IndexError:
                print 'No results available.'

    # menu showing functions
    @staticmethod
    def basic(button, *args):
        drop = DropDown(allow_sides=True, auto_width=False)
        for t in Basic.names:
            but = SizedButton(text=t[0])
            but.bind(on_release=t[1])
            drop.add_widget(but)
        drop.open(button)

    @staticmethod
    def avgs(button, *args):
        drop = DropDown(allow_sides=True, auto_width=False)
        for t in Avgs.names:
            but = SizedButton(text=t[0])
            but.bind(on_release=t[1])
            drop.add_widget(but)
        drop.open(button)

    @staticmethod
    def manipulate(button, *args):
        drop = DropDown(allow_sides=True, auto_width=False)
        for t in Manipulate.names:
            but = SizedButton(text=t[0])
            but.bind(on_release=t[1])
            drop.add_widget(but)
        drop.open(button)

    @staticmethod
    def about(*args):
        '''Displays `about` page of the app and includes other credits.

        .. versionadded:: 0.1.0
        '''
        aboutdlg = Popup(title='About')
        text = (
            'Copyright (C) 2016, KeyWeeUsr(Peter Badida)\n'
            'License: GNU GPL v3.0\n'
            'Find me @ https://github.com/KeyWeeUsr\n\n'
            'Used Software:\n\n'
            'Python\n'
            'Copyright (C) 2001-2016 Python Software Foundation\n'
            'All rights reserved.\n\n'
            'Kivy\n'
            'Copyright (C) 2010-2016 Kivy Team and other contributors\n\n'
            'NumPy\n'
            'Copyright (C) 2005-2016, NumPy Developers.\n'
            'All rights reserved.\n\n'
            'SciPy\n'
            'Copyright (C) 2003-2013 SciPy Developers.\n'
            'All rights reserved.\n\n'
            'MatPlotLib\n'
            'Copyright (C) 2002-2016 John D. Hunter\n'
            'All Rights Reserved\n'
        )

        aboutdlg.content = Label(text=text)
        aboutdlg.open()

    @staticmethod
    def test(*args):
        print 'ping: ', args

    # non-menu related functions
    @staticmethod
    def get_column(address):
        col = 0
        for c in address:
            if c in string.ascii_letters:
                col = col * 26 + (ord(c.upper()) - ord('A')) + 1
        return col

    def from_address(self, table, address, extended=False, *args):
        '''Gets value(s) from :mod:`main.Table` according to the address such as
        ``A1`` or ``A1:B2``. Values are fetched in the way that the final list
        contains even empty (``u''``) values. It is not expected of user to use
        :ref:`task` for strings and most of them won't even run. To get
        non-empty values for a :ref:`task` use for example Python's
        ``filter()``::

            values = filter(lambda x: len(str(x)), values)

        This `filter`, however, will remain values such as ``None`` untouched.

        .. versionadded:: 0.1.0

        .. versionchanged:: 0.3.5
           Added extended options and a possibility to get ``:all`` values from
           data.
        '''
        values = []
        col_row = []  # [column, row] such as [x, y] |_
        if ':' not in address:
            match = re.findall(r'([a-zA-Z]+)([0-9]+)', address)
            col_row.append([self.get_column(match[0][0]), match[0][1]])
        else:
            if 'all' in address:
                start_col = 1
                start_row = 1
                end_col = self.tables[table][1].cols
                end_row = self.tables[table][1].rows
            else:
                addresses = address.split(':')
                match = re.findall(r'([a-zA-Z]+)([0-9]+)', ' '.join(addresses))
                start_col = self.get_column(match[0][0])
                start_row = int(match[0][1])
                end_col = self.get_column(match[1][0])
                end_row = int(match[1][1])
            for col in range(start_col - 1, end_col):
                for row in range(start_row - 1, end_row):
                    col_row.append([col + 1, row + 1])

        col_range = 0
        row_range = 0
        val_place = [None, None]  # [column, row]
        table_cols = self.tables[table][1].cols
        table_rows = self.tables[table][1].rows
        labels = self.tables[table][1].labels

        while col_row:
            c, r = col_row.pop(0)
            c = int(c)
            r = int(r)

            if 0 < r < table_rows and 0 < c < table_cols:
                # increment ranges
                if extended:
                    if val_place[0] != c:
                        val_place[0] = c
                        col_range += 1
                    if val_place[1] != r:
                        val_place[1] = r
                        row_range += 1

                # get values
                key = table_cols * (r + 1) - (table_cols - c)
                item = self.tables[table][1].rv.data[key]
                if item['r'] == r and item['c'] == c:
                    if issubclass(item['type'], float):
                        values.append(float(item['text']))
                    elif issubclass(item['type'], int):
                        values.append(int(item['text']))
                    else:
                        values.append(item['text'])
        if extended:
            if row_range < col_range:
                # return 1 manually if only one row
                # otherwise row_range == 0
                row_range = 1
            else:
                row_range = row_range / int(col_range)
            return values, col_range, row_range, labels
        else:
            return values

    def set_page(self, task, result, result_type='text', footer='time'):
        '''Creates a :mod:`main.PageBox` for a result. The header consists of the
        :ref:`task`'s name, the footer is by default the time when the result
        was created and the content depends on `result_type` which can be -
        text, image(path to image) or widget. If `result_type == 'widget'`,
        result has to be an instance of a widget (obviously containing the
        output), e.g.::

            b = Button(text='my output')
            set_page('MyTask', b, result_type='widget')

        .. note:: When exporting pages, everything is converted into images
           (pngs), therefore making fancy behaving widgets is irrelevant.

        .. versionadded:: 0.2.0

        .. versionchanged:: 0.3.2
           Added tables as a result type.
        '''
        page = PageBox()
        head = PaperLabel(text=task, size_hint_y=None, height='30dp')

        if result_type == 'text':
            content = PaperLabel(text=result)
        elif result_type in ['image', 'import']:
            content = Image(source=result)
        elif 'table' in result_type:
            # result == list of values
            box = BoxLayout(orientation='vertical')
            grid = ResultGrid(cols=int(result_type.strip('table')),
                              padding=1, spacing=1, size_hint=[0.95, None],
                              pos_hint={'center_x': 0.5})
            grid.bind(minimum_height=grid.setter('height'))

            for value in result:
                grid.add_widget(Wrap(text=' ' + str(value), color=[0, 0, 0, 1],
                                     background_color=[1, 1, 1, 1]))

            box.add_widget(Widget())
            box.add_widget(grid)
            box.add_widget(Widget())
            content = box

        elif result_type == 'widget':
            content = result

        # turn off with footer=None
        if result_type == 'import':
            pass
        elif not footer:
            foot = PaperLabel(size_hint_y=None, height='30dp')
        else:
            if footer == 'time':
                t = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                foot = PaperLabel(text=t,
                                  size_hint_y=None,
                                  height='30dp')
            else:
                foot = PaperLabel(text=footer, size_hint_y=None,
                                  height='30dp')

        if not result_type == 'import':
            page.add_widget(head)
            page.add_widget(content)
            page.add_widget(foot)
        else:
            page.add_widget(content)
        self.ids.results.add_widget(page, 1)

        panel = self.ids.resultspanel
        if panel.width == panel.min_size:
            panel.width = panel.max_size

    @staticmethod
    def simple_chars(substring, from_undo):
        chars = re.findall(r'([a-zA-Z0-9.])', substring)
        return u''.join(chars)

    @staticmethod
    def address_chars(substring, from_undo):
        chars = re.findall(r'([a-zA-Z0-9:])', substring)
        return u''.join(chars)

    def update_tree(self, dt):
        tree = self.ids.tree
        lab = TreeViewLabel
        for node in tree.iterate_all_nodes():
            tree.remove_node(node)
        root = tree.add_node(lab(text=self.app.project_name, is_open=True))
        for path, folders, files in os.walk(self.app.project_dir):
            if op.basename(self.app.project_dir) != op.basename(path):
                dirname = op.basename(path).title()
                parent = tree.add_node(lab(text=dirname, is_open=True), root)
                for file in files:
                    filename = op.basename(file)
                    tree.add_node(lab(text=filename, is_open=True), parent)


class KrySA(App):
    '''The main class of the application through which is handled the
    communication of other classes with getting an instance of the app via
    ``App.get_running_app()``.

    Other than that, it holds important variables of :ref:`project`, sql
    blacklist for :ref:`sqlite` creating and updating or the application
    properties themselves.
    '''
    path = op.dirname(op.abspath(__file__))
    icon = path + '/data/icon.png'
    project_exists = BooleanProperty(False)
    project_name = ''
    project_dir = ''
    title = 'KrySA'
    errorcls = ErrorPop
    tablecls = Table
    sql_blacklist = ['DROP', 'EXEC', 'DECLARE', 'UPDATE', 'CREATE', 'DELETE',
                     'INSERT', 'JOIN', '=', '"', "'", ';']

    def on_project_exists(self, instance, exists):
        '''Checks change of :mod:`main.KrySA.project_exists` and if
        :ref:`project` exists, schedules updating of its tree to 5 second
        interval.

        .. versionadded:: 0.3.0
        '''
        if exists:
            self.treeclock = Clock.schedule_interval(self.root.update_tree, 5)
        else:
            Clock.unschedule(self.treeclock)

    def build(self):
        '''Default Kivy function for getting the root widget of application.
        '''
        # read MenuDrop if an idea of removing it comes up
        MenuDrop()
        return Body()

if __name__ == '__main__':
    KrySA().run()
