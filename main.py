# -*- coding: utf-8 -*-
# KrySA - Statistical analysis for rats
# Version: 0.1.4
# Copyright (C) 2016, KeyWeeUsr(Peter Badida) <keyweeusr@gmail.com>
# License: GNU GPL v3.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# More info in LICENSE.txt
#
# The above copyright notice, warning and additional info together with
# LICENSE.txt file shall be included in all copies or substantial portions
# of the Software.

from kivy.config import Config
# Config.set('graphics', 'window_state', 'maximized')
import re
import os
import json
import math
import numpy
import scipy
import string
import sqlite3
import os.path as op
from kivy.app import App
from functools import partial
from dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty


class ErrorPop(Popup):
    message = StringProperty('')

    def __init__(self, **kw):
        self.message = kw.get('msg', '')
        super(ErrorPop, self).__init__(**kw)


class NewDataValue(BoxLayout):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        super(NewDataValue, self).__init__(**kw)
        self.filter = kw['filter']


class NewDataColumn(BoxLayout):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        super(NewDataColumn, self).__init__(**kw)

    def free(self, items):
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
        msg = 'Please remove any SQL keyword present in the column!'

        for item in disable:
            if hasattr(item, 'disabled'):
                item.disabled = True
            else:
                # disable children
                for i in item:
                    i.disabled = True
        coltype = coltype.text

        # check for any sql keywords
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


class NewDataLayout(BoxLayout):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        super(NewDataLayout, self).__init__(**kw)


# remove unnecessary __init__ later
class SmallLargeLayout(BoxLayout):
    def __init__(self, **kw):
        super(SmallLargeLayout, self).__init__(**kw)


class CountLayout(BoxLayout):
    def __init__(self, **kw):
        super(CountLayout, self).__init__(**kw)


# inherit?
class Task(Popup):
    run = ObjectProperty(None)

    def __init__(self, **kw):
        super(Task, self).__init__(**kw)
        self.run = kw.get('run', None)
        wdg = kw.get('wdg', None)
        if wdg:
            self.ids.container.add_widget(wdg)

    def get_table_pos(self, text, values, *args):
        print values
        gen = (i for i, val in enumerate(values) if val == text)
        for i in gen:
            return i


class CreateWizard(Popup):
    run = ObjectProperty(None)

    def __init__(self, **kw):
        super(CreateWizard, self).__init__(**kw)
        self.run = kw.get('run', None)
        wdg = kw.get('wdg', None)
        if wdg:
            self.ids.container.add_widget(wdg)


class Dialog(Popup):
    confirm = StringProperty('')
    run = ObjectProperty(None)
    dirs = BooleanProperty(False)
    project = BooleanProperty(False)

    def __init__(self, **kw):
        super(Dialog, self).__init__(**kw)
        self.confirm = kw.get('confirm', '')
        self.run = kw.get('run', None)
        self.dirs = kw.get('dirs', False)
        self.project = kw.get('project', False)
        if self.project:
            self.ids.name.hint_text = 'project.krysa'
        else:
            self.ids.name.hint_text = 'example.sqlite'


class SideItem(BoxLayout):
    pass


class TableItem(TextInput):
    def update_value(self, txt, *args):
        data = []
        cols = self.cols - 1

        for i in self.origin.data:
            if 'cell' in i:
                data.append(i)
        chunks = [data[x:x+cols] for x in xrange(0, len(data), cols)]

        orig_type = type(chunks[self.r][self.c - 1])
        self.origin.data[self.cols*(self.r+1)-(self.cols-self.c)]['text'] = txt
        self.origin.refresh_from_data()


class Table(ScrollView):
    # use with ....add_widget(Table(max_cols=3, max_rows=3))
    # Grid -> Scroll, grid as container - better for sizing and placing

    # set "address" for table pos in grid to item
    number_size = (30, 30)
    default_size = (100, 30)

    def __init__(self, **kw):
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
        self.labels = kw.get('labels', None)
        self.types = kw.get('types', None)

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
                        self.rv.data.append({'text': '', 'disabled': True,
                                             'size': self.number_size,
                                             'origin': self.rv})
                    else:
                        self.rv.data.append({'text': self.labels[c-1]+ltr[c-1],
                                             '_text': self.labels[c-1],
                                             'disabled': True,
                                             'cell': 'label' + str(c-1),
                                             'type': type(''),
                                             'size': self.default_size,
                                             'origin': self.rv})
                else:
                    if c == 0:
                        self.rv.data.append({'text': str(r),
                                             'disabled': True,
                                             'size': self.number_size,
                                             'origin': self.rv})
                    else:
                        filter = None
                        try:
                            val = self.values.pop(0)
                            text_type = type(val)
                            filter_val = repr(text_type)[7:-2]
                            if filter_val == 'int' or filter_val == 'float':
                                filter = filter_val
                        except IndexError:
                            print 'values < space'
                            val = '.'

                        if 'e+' in str(val) or 'e-' in str(val):
                            val = '{0:.10f}'.format(val)
                        if hasattr(self, 'types'):
                            if self.types[c - 1] == 'INTEGER':
                                filter = 'int'
                                text_type = type(1)
                            elif self.types[c - 1] == 'REAL':
                                filter = 'float'
                                text_type = type(1.1)
                        self.rv.data.append({'text': str(val),
                                             'disabled': False,
                                             'cell': self.labels[c-1] + str(r),
                                             'r': r,
                                             'rows': self.rows,
                                             'c': c,
                                             'cols': self.cols,
                                             'type': text_type,
                                             'size': self.default_size,
                                             'input_filter': filter,
                                             'origin': self.rv})
        if self.values:
            raise Exception('Not enough space for all values! \
                            Increase rows/cols!')
        self.add_widget(self.rv)

    def get_letters(self):
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
        for i in self.rv.data:
            if 'cell' in i and 'label' not in i['cell']:
                i['disabled'] = disabled
        self.rv.refresh_from_data()

    def clean(self, *args):
        self.rv.data = []


class ProcessFlow(BoxLayout, StencilView):
    def __init__(self, **kw):
        super(ProcessFlow, self).__init__(**kw)
        app = App.get_running_app()
        self.texture = Image(source=app.path+'/grid.png').texture
        self.texture.wrap = 'repeat'


class SizedButton(Button):
    def correct_width(self, *args):
        self.width = self.texture_size[0] + 8
        self.parent.parent.width = max([c.width for c in self.parent.children])
        for child in self.parent.children:
            child.width = self.parent.parent.width


class MenuDrop(DropDown):
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
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.tables = []
        self.app.menu = {'file': (['New...', self.new],
                                  ['_Open', self.open],
                                  ['Close Project', self.close_project],
                                  ['_Save Project', self.save_project],
                                  ['_Save Project As...',
                                   self.save_project_as],
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
                                   ['Averages', self.avgs],),
                         'help': (['_KrySA Help', self.test],
                                  ['_Getting Started Tutorial', self.test],
                                  ['About KrySA', self.about],),
                         }
        super(Body, self).__init__(**kw)

    def new(self, button, *args):
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
        self.close_project()
        self.savedlg = Dialog(title='New Project',
                              confirm='Save',
                              run=self._save_project,
                              dirs=True,
                              project=True)
        self.savedlg.open()

    def _new_data(self, *args):
        if not self.app.project_exists:
            error = ErrorPop(msg='No project exists!')
            error.open()
            return
        widget = NewDataLayout()
        task = CreateWizard(title='New Data', wdg=widget,
                            run=partial(self._save_data, widget))
        task.open()

    def _save_data(self, wizard, *args):
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
                    values.append(u'')

        self.tables.append((table_name, Table(max_cols=max_cols,
                                              max_rows=max_rows, pos=self.pos,
                                              size=self.size, values=values,
                                              labels=labels, types=types)))
        tabletab.content = self.tables[-1][1]

        # export to data.sqlite in <project>/data directory
        data = op.join(self.app.project_dir, 'data')
        self._export_data([data], 'data.sqlite')

    def open(self, *args): pass

    def close_project(self, *args):
        # call this before a new project
        self.app.project_exists = False
        self.app.project_dir = ''
        tp = self.ids.tabpanel
        while len(tp.tab_list) > 1:
            tp.remove_widget(tp.tab_list[0])
        self.ids.flow.clear_widgets()
        tp.switch_to(tp.tab_list[0])

    def save_project(self, *args):
        # same as _new_project + export data & results
        self.savedlg = Dialog(title='New Project',
                              confirm='Save',
                              run=self._save_project,
                              dirs=True,
                              project=True)
        self.savedlg.open()

    def _save_project(self, selection, fname, *args):
        if not selection:
            return
        else:
            selection = selection[0]
        if '.' not in fname:
            fname = fname + '.krysa'

        try:
            os.mkdir(op.join(selection, fname.split('.')[0]))
            selection = op.join(selection, fname.split('.')[0])
            data = op.join(selection, 'data')
            results = op.join(selection, 'results')
            os.mkdir(data)
            os.mkdir(results)
            if op.exists(op.join(selection, fname)):
                os.remove(op.join(selection, fname))
        except OSError:
            error = ErrorPop(msg='Project folder already exists!')
            error.open()
            return

        self.app.project_exists = True
        self.app.project_dir = selection
        self.app.project_name = fname.split('.')[0]

        # (dummy for now)
        # dump widgets' properties from process flow to dict, then to json
        project = {'test': 'blah'}
        with open(op.join(selection, fname), 'wb') as f:
            f.write(json.dumps(project, indent=4))

        # let user set table columns, add to tab, then:
        self._export_data([data], 'data.sqlite')

        # exporting results still missing -> 0.2.x

    def save_project_as(self, *args): pass

    def import_data(self, *args):
        self.opendlg = Dialog(title='Import Data',
                              confirm='Import',
                              run=self._import_data)
        self.opendlg.open()

    def _import_data(self, selection, *args):
        # limit table name and column name to [a-zA-Z]

        # CREATE TABLE test(
        #                   Column INTEGER NOT NULL CHECK(
        #                               typeof(Column) = 'integer'))
        if not selection:
            return
        else:
            selection = selection[0]

        conn = sqlite3.connect(op.join(selection))
        c = conn.cursor()

        # get tables first!
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [tab[0] for tab in c.fetchall()]

        for table in tables:
            c.execute("pragma table_info(%s)" % table)
            table_info = c.fetchall()
            labels = [lbl[1] for lbl in table_info]
            types = [type[2][0] for type in table_info]
            # allow only: INTEGER, REAL, TEXT

            tabletab = TabbedPanelItem(text=table)
            self.ids.tabpanel.add_widget(tabletab)
            c.execute('select * from %s' % table)
            values = [item for item in c.fetchone()]
            max_cols = len(values)
            values += [item for sublist in c.fetchall() for item in sublist]
            max_rows = int(math.ceil(len(values)/float(max_cols)))
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

    def _extract_rows(self, data):
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
            columns = table[1].rv.data[1:max_cols+1]  # types need whole dict!
            types = table[1].rv.data[max_cols+2:2*(max_cols+1)]

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
            c.execute("CREATE TABLE "+table[0]+"("+col_string+")")
            rows = self._extract_rows(table[1].rv.data)[max_cols:]

            cnks = [rows[x:x+max_cols] for x in xrange(0, len(rows), max_cols)]
            for chunk in cnks:
                _chunk = []
                for cnk in chunk:
                    if not isinstance(cnk, (str, unicode)):
                        # switch to unicode???
                        _chunk.append(str(cnk))
                    else:
                        _chunk.append('\''+cnk+'\'')
                values = ','.join(_chunk)
                c.execute("INSERT INTO "+table[0]+" VALUES("+values+")")
            conn.commit()
        conn.close()
        self.savedlg.dismiss()

    def basic(self, button, *args):
        d = DropDown(allow_sides=True, auto_width=False)
        buttons = []
        buttons.append(SizedButton(text='Count'))
        buttons[0].bind(on_release=self.basic_count)
        buttons.append(SizedButton(text='_Count if'))
        buttons.append(SizedButton(text='Minimum'))
        buttons[2].bind(on_release=self.basic_min)
        buttons.append(SizedButton(text='Maximum'))
        buttons[3].bind(on_release=self.basic_max)
        buttons.append(SizedButton(text='Small'))
        buttons[4].bind(on_release=self.basic_small)
        buttons.append(SizedButton(text='Large'))
        buttons[5].bind(on_release=self.basic_large)
        buttons.append(SizedButton(text='_Frequency'))
        for b in buttons:
            d.add_widget(b)
        d.open(button)

    def basic_count(self, *args):
        widget = CountLayout()
        task = Task(title='Count', wdg=widget)
        task.run = partial(self._basic_count,
                           task,
                           task.ids.container.children[0].ids.name)
        task.open()

    def _basic_count(self, task, address, *args):
        values = self.from_address(task.tablenum, address.text)
        print len(values)

    def basic_countifs(self, *args): pass

    def basic_min(self, *args):
        widget = CountLayout()
        task = Task(title='Minimum', wdg=widget)
        task.run = partial(self._basic_min,
                           task,
                           task.ids.container.children[0].ids.name)
        task.open()

    def _basic_min(self, task, address, *args):
        values = self.from_address(task.tablenum, address.text)
        print values
        print min(values)

    def basic_max(self, *args):
        widget = CountLayout()
        task = Task(title='Maximum', wdg=widget)
        task.run = partial(self._basic_max,
                           task,
                           task.ids.container.children[0].ids.name)
        task.open()

    def _basic_max(self, task, address, *args):
        values = self.from_address(task.tablenum, address.text)
        print values
        print max(values)

    def basic_small(self, *args):
        widget = SmallLargeLayout()
        task = Task(title='Small', wdg=widget)
        task.run = partial(self._basic_small,
                           task,
                           task.ids.container.children[0].ids.name,
                           task.ids.container.children[0].ids.order)
        task.open()

    def _basic_small(self, task, address, k, *args):
        values = self.from_address(task.tablenum, address.text)
        values = sorted(values)
        print values
        try:
            print values[int(k.text)-1]
        except:
            pass

    def basic_large(self, *args):
        widget = SmallLargeLayout()
        task = Task(title='Large', wdg=widget)
        task.run = partial(self._basic_large,
                           task,
                           task.ids.container.children[0].ids.name,
                           task.ids.container.children[0].ids.order)
        task.open()

    def _basic_large(self, task, address, k, *args):
        values = self.from_address(task.tablenum, address.text)
        values = sorted(values, reverse=True)
        print values
        try:
            print values[int(k.text)-1]
        except:
            pass  # throw error k out of len(values) bounds, same for *_small

    def basic_freq(self, *args): pass

    def avgs(self, button, *args):
        d = DropDown(allow_sides=True, auto_width=False)
        buttons = []
        buttons.append(SizedButton(text='N - ic'))
        buttons.append(SizedButton(text='Quadratic'))
        # statistics.mean()
        buttons.append(SizedButton(text='Arithmetic'))
        # numpy.mean(values)
        buttons.append(SizedButton(text='Geometric'))
        # scipy.stats.gmean(values)
        buttons.append(SizedButton(text='Harmonic'))
        # scipy.stats.hmean(values)
        buttons.append(SizedButton(text='Interquartile'))
        # 1/2 * ( max(x) + min(x) )
        buttons.append(SizedButton(text='Midrange'))
        buttons.append(SizedButton(text='Generalized'))
        buttons.append(SizedButton(text='Trimmed'))
        # scipy.stats.tmean(values, limits)
        buttons.append(SizedButton(text='Median'))
        buttons.append(SizedButton(text='Mode'))
        buttons.append(SizedButton(text='Harmonic'))
        for b in buttons:
            d.add_widget(b)
        d.open(button)

    def about(self, *args):
        aboutdlg = Popup(title='About')
        text = ('Copyright (C) 2016, KeyWeeUsr(Peter Badida)\n'
                'License: GNU GPL v3.0\n'
                'Find me @ https://github.com/KeyWeeUsr')
        aboutdlg.content = Label(text=text)
        aboutdlg.open()

    # non-menu functions
    def get_column(self, address):
        col = 0
        for c in address:
            if c in string.ascii_letters:
                col = col * 26 + (ord(c.upper()) - ord('A')) + 1
        return col

    def from_address(self, table, address, *args):
        # allow using column name as address?
        values = []
        col_row = []  # [column, row] such as [x, y] |_
        if ':' not in address:
            match = re.findall(r'([a-zA-Z]+)([0-9]+)', address)
            col_row.append([self.get_column(match[0][0]), match[0][1]])
        else:
            addresses = address.split(':')
            match = re.findall(r'([a-zA-Z]+)([0-9]+)', ' '.join(addresses))
            start_col = self.get_column(match[0][0])
            start_row = int(match[0][1])
            end_col = self.get_column(match[1][0])
            end_row = int(match[1][1])
            col_range = end_col - start_col
            row_range = end_row - start_row
            for col in range(start_col-1, end_col):
                for row in range(start_row-1, end_row):
                    col_row.append([col + 1, row + 1])
                start_row = int(match[0][1])
        while col_row:
            c, r = col_row.pop(0)
            c = int(c)
            r = int(r)
            table_cols = self.tables[table][1].cols
            table_rows = self.tables[table][1].rows

            if r > 0 and c > 0 and r < table_rows and c < table_cols:
                key = table_cols * (r + 1) - (table_cols - c)
                item = self.tables[table][1].rv.data[key]
                if item['r'] == r and item['c'] == c:
                    if issubclass(item['type'], float):
                        values.append(float(item['text']))
                    elif issubclass(item['type'], int):
                        values.append(int(item['text']))
                    else:
                        values.append(item['text'])
        return values

    def test(self, *args):
        print 'ping: ', args


class KrySA(App):
    path = op.dirname(op.abspath(__file__))
    icon = path+'/icon.png'
    project_exists = False
    project_name = ''
    project_dir = ''
    title = 'KrySA'
    sql_blacklist = ['DROP', 'EXEC', 'DECLARE', 'UPDATE', 'CREATE', 'DELETE',
                     'INSERT', 'JOIN', '=', '"', "'", ';']

    def build(self):
        a = MenuDrop()
        return Body()

if __name__ == '__main__':
    KrySA().run()
