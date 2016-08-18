# -*- coding: utf-8 -*-
# KrySA - Statistical analysis for rats
# Version: 0.2.5
# Copyright (C) 2016, KeyWeeUsr(Peter Badida) <keyweeusr@gmail.com>
# License: GNU GPL v3.0, More info in LICENSE.txt

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
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.label import Label
from time import gmtime, strftime
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
from kivy.properties import StringProperty, ObjectProperty, \
                            BooleanProperty, ListProperty

import tasks
import tasks.basic
import tasks.avgs
from tasks import Task

class PageBox(BoxLayout):
    def __init__(self, **kwargs):
        super(PageBox, self).__init__(**kwargs)
        self.add_widget = self.ids.page.add_widget


class PaperLabel(Label):
    pass


class ImgButton(Button):
    source = StringProperty('')


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
                    if i.ids.value.text == '' and coltype.text == 'REAL':
                        i.ids.value.text = '0.0'
                    elif i.ids.value.text == '' and coltype.text == 'INTEGER':
                        i.ids.value.text = '0'


class NewDataLayout(BoxLayout):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        super(NewDataLayout, self).__init__(**kw)


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
    filter = ListProperty([])

    def __init__(self, **kw):
        super(Dialog, self).__init__(**kw)
        self.confirm = kw.get('confirm', '')
        self.run = kw.get('run', None)
        self.dirs = kw.get('dirs', False)
        self.project = kw.get('project', False)
        if self.project:
            self.ids.name.hint_text = 'Project.krysa'
            self.filter = [lambda folder, fname: fname.endswith('.krysa')]
        else:
            self.ids.name.hint_text = 'example.sqlite'
            self.filter = [lambda folder, fname: fname.endswith('.sqlite')]


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
                        self.rv.data.append({'text': u'', 'disabled': True,
                                             'size': self.number_size,
                                             'origin': self.rv})
                    else:
                        self.rv.data.append({'text': self.labels[c-1]+ltr[c-1],
                                             '_text': self.labels[c-1],
                                             'disabled': True,
                                             'cell': 'label' + str(c-1),
                                             'type': type(u''),
                                             'size': self.default_size,
                                             'origin': self.rv})
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
                            if filter_val == 'int' or filter_val == 'float':
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
                        self.rv.data.append({'text': unicode(val),
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
        self.texture = Image(source=app.path+'/data/grid.png').texture
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
                                   ['_Averages', self.avgs],),
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
        self.wiz_newdata = CreateWizard(title='New Data', wdg=widget,
                                        run=partial(self._save_data, widget))
        self.wiz_newdata.open()

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

        # importing results still missing -> 0.2.x

    def close_project(self, *args):
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
        self.savedlg = Dialog(title='New Project',
                              confirm='Save',
                              run=self._save_project,
                              dirs=True,
                              project=True)
        self.savedlg.open()

    def _save_project(self, selection=None, fname=None, *args):
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

        # exporting results still missing -> 0.2.x

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
            if '.sqlite' not in selection:
                return

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
                        _chunk.append(unicode(cnk))
                    else:
                        _chunk.append('\''+cnk+'\'')
                values = ','.join(_chunk)
                c.execute("INSERT INTO "+table[0]+" VALUES("+values+")")
            conn.commit()
        conn.close()
        self.savedlg.dismiss()

    def basic(self, button, *args):
        drop = DropDown(allow_sides=True, auto_width=False)
        for t in tasks.basic.names:
            but = SizedButton(text=t[0])
            but.bind(on_release=t[1])
            drop.add_widget(but)
        drop.open(button)

    def avgs(self, button, *args):
        drop = DropDown(allow_sides=True, auto_width=False)
        for t in tasks.avgs.names:
            but = SizedButton(text=t[0])
            but.bind(on_release=t[1])
            drop.add_widget(but)
        drop.open(button)

    def about(self, *args):
        aboutdlg = Popup(title='About')
        text = ('Copyright (C) 2016, KeyWeeUsr(Peter Badida)\n'
                'License: GNU GPL v3.0\n'
                'Find me @ https://github.com/KeyWeeUsr')
        aboutdlg.content = Label(text=text)
        aboutdlg.open()

    # non-menu functions
    @staticmethod
    def get_column(address):
        col = 0
        for c in address:
            if c in string.ascii_letters:
                col = col * 26 + (ord(c.upper()) - ord('A')) + 1
        return col

    def from_address(self, table, address, *args):
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

    def set_page(self, task, result, result_type='text', footer='time'):
        page = PageBox()
        head = PaperLabel(text=task, size_hint_y=None, height='30dp')

        if result_type == 'text':
            content = PaperLabel(text=result)
        elif result_type == 'graph':
            content = Image(source=result)

        # turn off with footer=None
        if not footer:
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
        page.add_widget(head)
        page.add_widget(content)
        page.add_widget(foot)
        self.ids.results.add_widget(page, 1)

    @staticmethod
    def simple_chars(substring, from_undo):
        chars = re.findall(r'([a-zA-Z0-9.])', substring)
        return u''.join(chars)

    def test(self, *args):
        print 'ping: ', args


class KrySA(App):
    path = op.dirname(op.abspath(__file__))
    icon = path+'/data/icon.png'
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
