'''
.. toctree::
   mod_krysa_tasks_basic
   mod_krysa_tasks_avgs
'''

from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
import re
import os.path as op

Builder.load_file(op.join(op.dirname(op.abspath(__file__)), 'tasks.kv'))


class AddressLayout(BoxLayout):
    '''Simple layout that consists of single restricted input widget fetching
    only ``[a-zA-Z0-9:]`` values i.e. address.
    '''


class SmallLargeLayout(BoxLayout):
    '''A layout that consists of multiple restricted input widgets for address
    and `k` value.
    '''


class AvgsLayout(BoxLayout):
    '''A layout that consists of multiple restricted input widgets for address
    and `p` (power) value for the formula of generalized mean.
    '''
    def floatfilter(self, substring, from_undo):
        '''A function filtering everything that is not `-` symbol, floating
        point symbol(`.`) or a number.
        '''
        txt = self.ids.power.text
        if '-' in txt and '.' not in txt:
            chars = re.findall(r'([0-9.])', substring)
        elif '.' in txt:
            if '-' not in txt:
                chars = re.findall(r'([\-0-9])', substring)
            else:
                chars = re.findall(r'([0-9])', substring)
        else:
            chars = re.findall(r'([\-0-9.])', substring)
        return u''.join(chars)


class FreqLayout(BoxLayout):
    '''A layout that consists of multiple checkboxes and restricted input
    widgets for address, type of values, type of output frequency and
    limits of the input values.
    '''


class SortLayout(BoxLayout):
    '''Docs.
    '''

class Task(Popup):
    '''A popup handling the basic choosing of :ref:`data` from available
    :ref:`sqlite` in the application.
    '''
    run = ObjectProperty(None)

    def __init__(self, **kw):
        '''docs
        '''
        super(Task, self).__init__(**kw)
        self.app = App.get_running_app()
        self.run = kw.get('run')
        wdg = kw.get('wdg')
        self.call = kw.get('call')
        self.from_address = self.app.root.from_address
        self.set_page = self.app.root.set_page
        if wdg:
            self.ids.container.add_widget(wdg)

    def recalc_height(self, body, content):
        '''Recalculates the height of :mod:`tasks.Task` after a layout is
        added, so that the children are clearly visible without any stretching.
        '''
        confirms = self.ids.confirms
        content.height = sum([child.height for child in content.children])
        body.height = sum([child.height for child in body.children])
        self.height = body.height + confirms.height + self.separator_height

    @staticmethod
    def get_table_pos(text, values, *args):
        '''docs
        '''
        gen = (i for i, val in enumerate(values) if val == text)
        for i in gen:
            return i

    def try_run(self, *args):
        '''Tries to run a :ref:`task` from the input a user specified and
        closes the popup. If no such an action is possible, it'll show a popup
        with an error and leave :mod:`tasks.Task` opened.
        '''
        try:
            self.run(*args)
            if self.call:
                but = Button(size_hint_y=None, height='25dp',
                             text=self.call[0])
                but.bind(on_release=self.call[1])
                self.app.root.ids.recenttasks.add_widget(but)
            self.dismiss()
        except Exception as err:
            Logger.exception(err)
            error = self.app.errorcls(msg=repr(err))
            error.open()
