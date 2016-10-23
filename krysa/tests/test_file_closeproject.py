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

        # set columns for new data
        cols = new_data.ids.columns.children
        new_data.ids.columnadd.dispatch('on_release')
        cols[0].ids.colname.text += str(len(cols))
        cols[0].ids.coltype.text = 'INTEGER'
        vals = cols[0].ids.vals.children
        for i in range(5):
            cols[0].ids.valadd.dispatch('on_release')
            if i != 4:
                vals[0].ids.value.text = ''
            else:
                vals[0].ids.value.text = '1'

        new_data.ids.columnadd.dispatch('on_release')
        cols[0].ids.colname.text += str(len(cols))
        cols[0].ids.coltype.text = 'TEXT'
        vals = cols[0].ids.vals.children
        for i in range(3):
            cols[0].ids.valadd.dispatch('on_release')
            if i != 2:
                vals[0].ids.value.text = ''
            else:
                vals[0].ids.value.text = 'end'

        new_data.ids.columnadd.dispatch('on_release')
        cols[0].ids.colname.text += str(len(cols))
        cols[0].ids.coltype.text = 'REAL'
        vals = cols[0].ids.vals.children
        for i in range(4):
            cols[0].ids.valadd.dispatch('on_release')
            if i != 3:
                vals[0].ids.value.text = ''
            else:
                vals[0].ids.value.text = '1.1'
        new_data = app.root.wiz_newdata.run()

        # test project variables
        self.assertTrue(app.project_exists)
        self.assertFalse(app.project_dir is '')
        self.assertFalse(app.project_name is '')

        # test closed project
        app.root.close_project()

        self.assertFalse(app.project_exists)
        self.assertTrue(app.project_dir is '')
        self.assertTrue(app.project_name is '')
        self.assertFalse(app.root.tables)
        self.assertFalse(app.root.ids.flow.children)
        self.assertTrue(len(app.root.ids.tabpanel.tab_list) is 1)

        app.stop()

    def test_file_closeproject(self):
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
