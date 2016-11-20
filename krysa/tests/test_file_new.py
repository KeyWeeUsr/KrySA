from __future__ import print_function
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

# Py3 fixes
if sys.version_info[0] >= 3:
    xrange = range


class Test(unittest.TestCase):
    def pause(*args):
        time.sleep(0.000001)

    def run_test(self, app, *args):
        Clock.schedule_interval(self.pause, 0.000001)

        # test if there is error popup for no Project available
        app.root._new_data()
        children = [str(c) for c in app.root.parent.children]
        self.assertTrue(any('ErrorPop' in c for c in children))
        for c in children:
            if 'ErrorPop' in c:
                app.root.parent.children[children.index(c)].dismiss()

        # open New -> Project popup, set inputs
        app.root._new_project()
        app.root.savedlg.view.selection = [self.folder, ]
        app.root.savedlg.ids.name.text = 'Test.krysa'
        app.root.savedlg.run([self.folder, ], 'Test.krysa')
        project_folder = op.join(self.path, 'test_folder', 'Test')
        data = op.join(project_folder, 'data')
        results = op.join(project_folder, 'results')

        # tests Project tree
        self.assertTrue(op.exists(op.join(project_folder, 'Test.krysa')))
        self.assertTrue(op.exists(op.join(data, 'data.sqlite')))
        self.assertTrue(op.exists(results))

        # open New -> Data popup, set inputs
        app.root._new_data()
        new_data = app.root.wiz_newdata.ids.container.children[0]
        new_data.ids.table_name.text = 'NewData'

        # test removing a value and a column
        cols = new_data.ids.columns.children
        new_data.ids.columnadd.dispatch('on_release')
        cols[0].ids.valadd.dispatch('on_release')
        vals = cols[0].ids.vals.children

        vals[0].ids.valX.dispatch('on_release')
        self.assertFalse(vals)
        cols[0].ids.colX.dispatch('on_release')
        self.assertFalse(cols)

        # set columns for new data
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

        # create second data/sql table
        app.root._new_data()
        new_data = app.root.wiz_newdata.ids.container.children[0]
        new_data.ids.table_name.text = 'NewData2'
        cols = new_data.ids.columns.children

        new_data.ids.columnadd.dispatch('on_release')
        cols[0].ids.colname.text += str(len(cols))
        cols[0].ids.coltype.text = 'INTEGER'
        vals = cols[0].ids.vals.children
        cols[0].ids.valadd.dispatch('on_release')
        vals[0].ids.value.text = '1'

        new_data.ids.columnadd.dispatch('on_release')
        cols[0].ids.colname.text += str(len(cols))
        cols[0].ids.coltype.text = 'TEXT'
        vals = cols[0].ids.vals.children
        cols[0].ids.valadd.dispatch('on_release')
        vals[0].ids.value.text = 'text'

        new_data.ids.columnadd.dispatch('on_release')
        cols[0].ids.colname.text += str(len(cols))
        cols[0].ids.coltype.text = 'REAL'
        vals = cols[0].ids.vals.children
        cols[0].ids.valadd.dispatch('on_release')
        vals[0].ids.value.text = '1.1'
        new_data = app.root.wiz_newdata.run()

        # set testing data
        newdata_values = [[0, u'', 0.0],
                          [0, u'', 0.0],
                          [0, u'end', 0.0],
                          [0, u'', 1.1],
                          [1, u'', 0.0]]
        newdata2_values = [[1, u'text', 1.1]]

        # get data from krysa table
        ndv = []
        for d in app.root.tables[0][1].rv.data:
            if 'c' in d.keys():
                if d['type'] == int:
                    ndv.append(int(d['text']))
                elif d['type'] == float:
                    ndv.append(float(d['text']))
                else:
                    ndv.append(d['text'])
        ndv = [ndv[x:x + 3] for x in xrange(0, len(ndv), 3)]

        ndv2 = []
        for d in app.root.tables[1][1].rv.data:
            if 'c' in d.keys():
                if d['type'] == int:
                    ndv2.append(int(d['text']))
                elif d['type'] == float:
                    ndv2.append(float(d['text']))
                else:
                    ndv2.append(d['text'])
        ndv2 = [ndv2[x:x + 3] for x in xrange(0, len(ndv2), 3)]

        # test data
        self.assertTrue(op.exists(op.join(data, 'data.sqlite')))
        conn = sqlite3.connect(op.join(data, 'data.sqlite'))
        c = conn.cursor()
        c.execute('SELECT * FROM NewData')
        values = [item for sublist in c.fetchall() for item in sublist]
        values = [values[x:x + 3] for x in xrange(0, len(values), 3)]
        conn.close()
        print('NewData:')
        for i, v in enumerate(values):
            # values == sql values
            self.assertEqual(v, newdata_values[i])
            # values == KrySA values
            self.assertEqual(ndv[i], newdata_values[i])
            print(v)

        conn = sqlite3.connect(op.join(data, 'data.sqlite'))
        c = conn.cursor()
        c.execute('SELECT * FROM NewData2')
        values = [item for sublist in c.fetchall() for item in sublist]
        values = [values[x:x + 3] for x in xrange(0, len(values), 3)]
        conn.close()
        print('\nNewData2:')
        for i, v in enumerate(values):
            self.assertEqual(v, newdata2_values[i])
            self.assertEqual(ndv2[i], newdata2_values[i])
            print(v)

        app.stop()

    def test_file_new(self):
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
