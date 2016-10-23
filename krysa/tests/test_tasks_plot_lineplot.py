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
from tasks.plot import Plot


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
        address = ['A1:D13', 'A1:B2', 'C1:D2',
                   'A12:B13', 'C12:D13', 'B3:C10']
        for addr in address:
            for xonly in range(2):
                taskcls = Plot()
                taskcls.plot_line()

                children = app.root_window.children
                for c in children:
                    if 'Task' in str(c):
                        index = children.index(c)
                task = children[index]

                # fill the task
                body = task.children[0].children[0].children[0].children
                body[-1].text = 'NewData'
                body[-2].children[0].children[-1].text = 'Test Title'

                # fetching addresses and axes labels
                box_values = body[-2].children[0].children[-2]
                box_values.children[-1].children[-2].text = addr
                body[-2].children[0].children[-3].children[0].active = True
                if not xonly:
                    box_values.children[-2].children[-2].text = addr

                # set axes limits
                box_values = body[-2].children[0].children[-5]
                box_values.children[-1].children[-1].text = '-20'
                box_values.children[-1].children[0].text = '20'

                # set line options
                box_values.children[-2].children[-3].text = 'g'
                box_values.children[-2].children[-4].text = 's'
                box_values.children[-3].children[0].active = True
                body[-3].children[0].dispatch('on_release')

        # get results and test
        res_dir = op.join(app.project_dir, 'plots')
        result = len([f for f in os.listdir(res_dir) if f.startswith('plot')])
        self.assertEqual(result, 12)

        results = app.root.ids.results
        skipone = False  # if top padding with widget present
        for c in reversed(results.children):
            if 'Widget' in str(c):
                skipone = True
                break
        results = len(results.children)
        self.assertEqual(results - 1 if skipone else results, 12)
        app.stop()

    def test_tasks_plot_lineplot(self):
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
