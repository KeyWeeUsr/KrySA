import unittest

import os
import sys
import time
import sqlite3
import os.path as op
from shutil import rmtree
from functools import partial
from kivy.clock import Clock

main_path = op.dirname(op.dirname(op.abspath(__file__)))
sys.path.append(main_path)
from main import KrySA, ErrorPop
from tasks.basic import Basic


class Test(unittest.TestCase):
    def pause(*args):
        time.sleep(0.000001)

    def run_test(self, app, *args):
        Clock.schedule_interval(self.pause, 0.000001)

        # open New -> Project popup, set inputs
        app.root._new_project()
        app.root.savedlg.view.selection = [self.folder, ]
        app.root.savedlg.ids.name.text = 'Test.krysa'
        app.root.savedlg.run([self.folder, ], 'Test.krysa')
        project_folder = op.join(self.path, 'test_folder', 'Test')
        data = op.join(project_folder, 'data')
        results = op.join(project_folder, 'results')

        # open New -> Data popup, set inputs
        app.root._new_data()
        new_data = app.root.wiz_newdata.ids.container.children[0]
        new_data.ids.table_name.text = 'NewData'
        cols = new_data.ids.columns.children

        # set columns for new data
        range_vals = range(13)
        for _ in range(2):
            new_data.ids.columnadd.dispatch('on_release')
            cols[0].ids.colname.text += str(len(cols))
            cols[0].ids.coltype.text = 'INTEGER'
            vals = cols[0].ids.vals.children

            for i in range_vals:
                cols[0].ids.valadd.dispatch('on_release')
                vals[0].ids.value.text = str(i + 1)

            new_data.ids.columnadd.dispatch('on_release')
            cols[0].ids.colname.text += str(len(cols))
            cols[0].ids.coltype.text = 'REAL'
            vals = cols[0].ids.vals.children

            for i in range_vals:
                cols[0].ids.valadd.dispatch('on_release')
                num = str(i + 1)
                vals[0].ids.value.text = num + '.' + num
        new_data = app.root.wiz_newdata.run()

        # open Task's popup and get task
        conditions = [
            ['Equal to', '1'],
            ['Not equal to', '13'],
            ['Less than', '10.10'],
            ['Less than or equal', '10'],
            ['Greater than', '4.4'],
            ['Greater than or equal', '5'],
            ['Less than&,Greater than or equal|,Equal to', '13.13,10,1']
        ]

        for con in conditions:
            taskcls = Basic()
            taskcls.basic_countif()

            children = app.root_window.children
            for c in reversed(children):
                if 'Task' in str(c):
                    index = children.index(c)
            task = children[index]

            # fill the task
            body = task.children[0].children[0].children[0].children
            add_cond = body[-2].children[0].children[-1].children[0]
            conds = body[-2].children[0].children[-2].children[0]
            body[-1].text = 'NewData'
            body[-2].children[0].children[-1].children[-2].text = 'A1:D13'

            # if multiple conditions
            if ',' in con[0]:
                cs = con[0].split(',')
                vs = con[1].split(',')
                for i in range(len(cs)):
                    add_cond.dispatch('on_release')
                    conds.children[0].children[-2].text = vs[i]
                    if '&' in cs[i]:
                        conds.children[0].children[-3].text = 'AND'
                        conds.children[0].children[-1].text = cs[i][:-1]
                    elif '|' in cs[i]:
                        conds.children[0].children[-3].text = 'OR'
                        conds.children[0].children[-1].text = cs[i][:-1]
                    else:
                        conds.children[0].children[-1].text = cs[i]

            else:
                add_cond.dispatch('on_release')
                conds.children[0].children[-1].text = con[0]
                conds.children[0].children[-2].text = con[1]

            body[-3].children[0].dispatch('on_release')

        # get results and test
        expected = reversed([2, 50, 38, 38, 36, 36, 16])
        results = app.root.ids.results
        skipone = False  # if top padding with widget present
        for c in results.children:
            if 'Widget' in str(c):
                skipone = True
                break

        for i, exp in enumerate(expected):
            i = i + 1 if skipone else i
            # Result -> Page -> container -> result
            result = int(results.children[i].ids.page.children[1].text[-2:])
            self.assertEqual(result, exp)
        app.stop()

    def test_tasks_basic_countif(self):
        self.path = op.dirname(op.abspath(__file__))
        if not op.exists(op.join(self.path, 'test_folder')):
            os.mkdir(op.join(self.path, 'test_folder'))
        else:
            rmtree(op.join(self.path, 'test_folder'))
            os.mkdir(op.join(self.path, 'test_folder'))
        self.folder = op.join(self.path, 'test_folder')

        app = KrySA()
        p = partial(self.run_test, app)
        Clock.schedule_once(p, .000001)
        app.run()
        rmtree(self.folder)

if __name__ == '__main__':
    unittest.main()
