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

Builder.load_string("""
<SingleTI@TextInput>:
    multiline: False
    input_filter: app.root.address_chars

<Task>:
    size_hint: 0.5, None
    pos_hint: {'center': [0.5, 0.5]}
    BoxLayout:
        id: taskbody
        orientation: 'vertical'
        Spinner:
            id: tablesel
            text: 'Choose data:'
            values: [child[0] for child in app.root.tables]
            size_hint_y: None
            height: dp(60)
            on_text:
                root.tablenum = root.get_table_pos(self.text, self.values)

        BoxLayout:
            id: container
            size_hint_y: None
            on_children: root.recalc_height(taskbody, self)

        BoxLayout:
            id: confirms
            size_hint_y: None
            height: dp(60)
            Button:
                text: 'Cancel'
                on_release: root.dismiss()

            Button:
                text: 'Run'
                disabled: True if tablesel.text == '' else False
                on_release: root.try_run()

<CountLayout>:
    orientation: 'vertical'
    SingleTI:
        id: name

<SmallLargeLayout>:
    orientation: 'vertical'
    BoxLayout:
        Label:
            text: 'Address'

        SingleTI:
            id: name

    BoxLayout:
        Label:
            text: 'k ='

        SingleTI:
            id: order

    Label:
        text: 'Example: k=2 for the second smallest value.'

<AvgsLayout>:
    orientation: 'vertical'
    BoxLayout:
        Label:
            text: 'Address'

        SingleTI:
            id: name

    BoxLayout:
        Label:
            text: 'p ='

        SingleTI:
            id: power
            input_filter: root.floatfilter

    Label:
        text: 'Example: p=0 for the geometric mean\\np=1 for the arithmetic.'

<FreqLayout>:
    size_hint_y: None
    height: dp(170)
    orientation: 'vertical'
    BoxLayout:
        Label:
            text: 'Address'

        SingleTI:
            id: name

        Label:
            text: 'Intervals'

        CheckBox:
            id: intervals

    BoxLayout:
        BoxLayout:
            BoxLayout:
                size_hint_x: None
                width: dp(80)
                Label:
                    text: 'Auto'

                CheckBox:
                    id: bins_auto
                    active: True
                    on_active: bins.disabled = True if self.active else False

            SingleTI:
                id: bins
                disabled: True
                hint_text: 'Number of bins'
                input_filter: 'int'

        BoxLayout:
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: None
                width: dp(80)
                BoxLayout:
                    Label:
                        text: 'Auto'

                    CheckBox:
                        id: limits_auto
                        active: True
                        on_active:
                            lowlimit.disabled = True if self.active else False
                            uplimit.disabled = True if self.active else False

            BoxLayout:
                orientation: 'vertical'
                SingleTI:
                    id: lowlimit
                    disabled: True
                    hint_text: 'Lower limit (default = 0)'
                    input_filter: 'float'

                SingleTI:
                    id: uplimit
                    disabled: True
                    hint_text: 'Upper limit (default = max + 1)'
                    input_filter: 'float'

    BoxLayout:
        Label:
            text: 'Type:'

        BoxLayout:
            Label:
                text: 'absolute'

            CheckBox:
                id: absolute
                active: True

        BoxLayout:
            Label:
                text: 'relative'

            CheckBox:
                id: relative
                active: True

        BoxLayout:
            Label:
                text: 'cumulative'

            CheckBox:
                id: cumulative
                active: True
""")


class CountLayout(BoxLayout):
    pass


class SmallLargeLayout(BoxLayout):
    pass


class AvgsLayout(BoxLayout):
    def floatfilter(self, substring, from_undo):
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
    pass


class Task(Popup):
    run = ObjectProperty(None)

    def __init__(self, **kw):
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
        confirms = self.ids.confirms
        content.height = sum([child.height for child in content.children])
        body.height = sum([child.height for child in body.children])
        self.height = body.height + confirms.height + self.separator_height

    @staticmethod
    def get_table_pos(text, values, *args):
        gen = (i for i, val in enumerate(values) if val == text)
        for i in gen:
            return i

    def try_run(self, *args):
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
