from __future__ import print_function
import unittest

import os
import sys
import time
import sqlite3
import os.path as op
from functools import partial
from kivy.clock import Clock

main_path = op.dirname(op.dirname(op.abspath(__file__)))
sys.path.append(main_path)
from main import KrySA

# Py3 fixes
if sys.version_info[0] >= 3:
    xrange = range


class Test(unittest.TestCase):
    def pause(*args):
        time.sleep(0.000001)

    def run_test(self, app, *args):
        Clock.schedule_interval(self.pause, 0.000001)

        # set testing data
        newdata_values = [[0, u'', 0.0],
                          [0, u'', 0.0],
                          [0, u'end', 0.0],
                          [0, u'', 1.1],
                          [1, u'', 0.0]]
        newdata2_values = [[1, u'text', 1.1]]

        app.root.import_data()
        app.root._import_data([op.join(self.path, 'test_Project',
                                       'data', 'data.sqlite')])

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
        self.assertTrue(op.exists(op.join(self.path, 'test_Project',
                                          'data', 'data.sqlite')))
        conn = sqlite3.connect(op.join(self.path, 'test_Project',
                                       'data', 'data.sqlite'))
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

        conn = sqlite3.connect(op.join(self.path, 'test_Project',
                                       'data', 'data.sqlite'))
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

    def test_file_importdata(self):
        self.path = op.dirname(op.abspath(__file__))

        app = KrySA()
        p = partial(self.run_test, app)
        Clock.schedule_once(p, .000001)
        app.run()

if __name__ == '__main__':
    unittest.main()
