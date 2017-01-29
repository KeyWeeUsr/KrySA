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
        range_vals = range(1, 31)
        new_data.ids.columnadd.dispatch('on_release')
        cols[0].ids.colname.text += str(len(cols))
        cols[0].ids.coltype.text = 'INTEGER'
        vals = cols[0].ids.vals.children

        for i in range_vals:  # -13 to -390
            cols[0].ids.valadd.dispatch('on_release')
            vals[0].ids.value.text = str(i * -13)

        new_data.ids.columnadd.dispatch('on_release')
        cols[0].ids.colname.text += str(len(cols))
        cols[0].ids.coltype.text = 'REAL'
        vals = cols[0].ids.vals.children

        for i in range_vals:  # 0.318.. to 9.554..
            cols[0].ids.valadd.dispatch('on_release')
            vals[0].ids.value.text = str(i / 3.14)

        new_data.ids.columnadd.dispatch('on_release')
        cols[0].ids.colname.text += str(len(cols))
        cols[0].ids.coltype.text = 'INTEGER'
        vals = cols[0].ids.vals.children

        for i in range_vals:  # 7 to 210
            cols[0].ids.valadd.dispatch('on_release')
            vals[0].ids.value.text = str(i * 7)

        new_data.ids.columnadd.dispatch('on_release')
        cols[0].ids.colname.text += str(len(cols))
        cols[0].ids.coltype.text = 'REAL'
        vals = cols[0].ids.vals.children

        for i in range_vals:  # 10.10 to 213.213
            cols[0].ids.valadd.dispatch('on_release')
            num = str(i * 7 + 3)
            vals[0].ids.value.text = num + '.' + num
        # create new data
        new_data = app.root.wiz_newdata.run()

        # open Task's popup and get task
        address = ['A1', 'A1:D30']

        for bintype in ('Count', 'Edges', 'Calculate'):
            for manual in range(2):
                for addr in address:
                    taskcls = Basic()
                    taskcls.basic_freq()

                    children = app.root_window.children
                    for c in reversed(children):
                        if 'Task' in str(c):
                            index = children.index(c)
                    task = children[index]

                    # fill the task
                    body = task.children[0].children[0].children[0].children
                    body[-1].text = 'NewData'
                    rows = body[-2].children[0].children

                    # address & precision
                    rows[-1].children[-2].text = addr
                    rows[-1].children[-4].text = '4'

                    # limits
                    if manual:
                        rows[-2].children[-2].children[0].active = False
                        rows[-2].children[-3].children[-1].text = '-300'
                        rows[-2].children[-3].children[-2].text = '500'

                    # bins
                    rows[-3].children
                    rows[-3].children[-2].text = bintype
                    screen = rows[-3].children[-3].children[0]

                    if bintype == 'Count':
                        # manually set 9 bins
                        screen.children[0].text = '9'

                    elif bintype == 'Edges':
                        # set bin edges from -100.14 to 799.86 wide 100
                        grid = screen.children[0].children[-1].children[0]
                        delbutton = screen.children[0].children[-3]
                        while grid.children:
                            delbutton.dispatch('on_release')
                        button = screen.children[0].children[-2]
                        for j in range(10):
                            button.dispatch('on_release')
                            grid.children[0].text = str(-100.14 + j * 100)

                    elif bintype == 'Calculate':
                        screen.children[0].children[-1].text = 'Scott'

                    # run task
                    body[-3].children[0].dispatch('on_release')

        # get results and test
        # 2x Count with auto limits
        # 2x Count with manual limits
        # 2x Edges with auto limits
        # 2x Edges with manual limits
        # 2x Calcu with auto limits
        # 2x Calcu with manual limits
        expected = [
            ['Lower edge', 'Upper edge', 'Absolute', 'Relative', 'Cumulative',
             '-13.5', '-13.3889', '0.0', '0.0', '0.0',
             '-13.3889', '-13.2778', '0.0', '0.0', '0.0',
             '-13.2778', '-13.1667', '0.0', '0.0', '0.0',
             '-13.1667', '-13.0556', '0.0', '0.0', '0.0',
             '-13.0556', '-12.9444', '1.0', '1.0', '1.0',
             '-12.9444', '-12.8333', '0.0', '0.0', '1.0',
             '-12.8333', '-12.7222', '0.0', '0.0', '1.0',
             '-12.7222', '-12.6111', '0.0', '0.0', '1.0',
             '-12.6111', '-12.5', '0.0', '0.0', '1.0'],
            ['Lower edge', 'Upper edge', 'Absolute', 'Relative', 'Cumulative',
             '-390.0', '-322.9763', '6.0', '0.05', '0.05',
             '-322.9763', '-255.9527', '5.0', '0.0417', '0.0917',
             '-255.9527', '-188.929', '5.0', '0.0417', '0.1334',
             '-188.929', '-121.9053', '5.0', '0.0417', '0.1751',
             '-121.9053', '-54.8817', '5.0', '0.0417', '0.2168',
             '-54.8817', '12.142', '36.0', '0.3', '0.5168',
             '12.142', '79.1657', '19.0', '0.1583', '0.6751',
             '79.1657', '146.1893', '19.0', '0.1583', '0.8334',
             '146.1893', '213.213', '20.0', '0.1667', '1.0001'],
            ['Lower edge', 'Upper edge', 'Absolute', 'Relative', 'Cumulative',
             '-300.0', '-211.1111', '0.0', '0.0', '0.0',
             '-211.1111', '-122.2222', '0.0', '0.0', '0.0',
             '-122.2222', '-33.3333', '0.0', '0.0', '0.0',
             '-33.3333', '55.5556', '1.0', '1.0', '1.0',
             '55.5556', '144.4444', '0.0', '0.0', '1.0',
             '144.4444', '233.3333', '0.0', '0.0', '1.0',
             '233.3333', '322.2222', '0.0', '0.0', '1.0',
             '322.2222', '411.1111', '0.0', '0.0', '1.0',
             '411.1111', '500.0', '0.0', '0.0', '1.0'],
            ['Lower edge', 'Upper edge', 'Absolute', 'Relative', 'Cumulative',
             '-300.0', '-211.1111', '7.0', '0.0583', '0.0583',
             '-211.1111', '-122.2222', '7.0', '0.0583', '0.1166',
             '-122.2222', '-33.3333', '7.0', '0.0583', '0.1749',
             '-33.3333', '55.5556', '46.0', '0.3833', '0.5582',
             '55.5556', '144.4444', '26.0', '0.2167', '0.7749',
             '144.4444', '233.3333', '20.0', '0.1667', '0.9416',
             '233.3333', '322.2222', '0.0', '0.0', '0.9416',
             '322.2222', '411.1111', '0.0', '0.0', '0.9416',
             '411.1111', '500.0', '0.0', '0.0', '0.9416'],
            ['Lower edge', 'Upper edge', 'Absolute', 'Relative', 'Cumulative',
             '-100.14', '-0.14', '1.0', '1.0', '1.0',
             '-0.14', '99.86', '0.0', '0.0', '1.0',
             '99.86', '199.86', '0.0', '0.0', '1.0',
             '199.86', '299.86', '0.0', '0.0', '1.0',
             '299.86', '399.86', '0.0', '0.0', '1.0',
             '399.86', '499.86', '0.0', '0.0', '1.0',
             '499.86', '599.86', '0.0', '0.0', '1.0',
             '599.86', '699.86', '0.0', '0.0', '1.0',
             '699.86', '799.86', '0.0', '0.0', '1.0'],
            ['Lower edge', 'Upper edge', 'Absolute', 'Relative', 'Cumulative',
             '-390.0', '-100.14', '23.0', '0.1917', '0.1917',
             '-100.14', '-0.14', '7.0', '0.0583', '0.25',
             '-0.14', '99.86', '57.0', '0.475', '0.725',
             '99.86', '199.86', '29.0', '0.2417', '0.9667',
             '199.86', '299.86', '4.0', '0.0333', '1.0',
             '299.86', '399.86', '0.0', '0.0', '1.0',
             '399.86', '499.86', '0.0', '0.0', '1.0',
             '499.86', '599.86', '0.0', '0.0', '1.0',
             '599.86', '699.86', '0.0', '0.0', '1.0',
             '699.86', '799.86', '0.0', '0.0', '1.0'],
            ['Lower edge', 'Upper edge', 'Absolute', 'Relative', 'Cumulative',
             '-100.14', '-0.14', '1.0', '1.0', '1.0',
             '-0.14', '99.86', '0.0', '0.0', '1.0',
             '99.86', '199.86', '0.0', '0.0', '1.0',
             '199.86', '299.86', '0.0', '0.0', '1.0',
             '299.86', '399.86', '0.0', '0.0', '1.0',
             '399.86', '499.86', '0.0', '0.0', '1.0',
             '499.86', '599.86', '0.0', '0.0', '1.0',
             '599.86', '699.86', '0.0', '0.0', '1.0',
             '699.86', '799.86', '0.0', '0.0', '1.0'],
            ['Lower edge', 'Upper edge', 'Absolute', 'Relative', 'Cumulative',
             '-390.0', '-100.14', '23.0', '0.1917', '0.1917',
             '-100.14', '-0.14', '7.0', '0.0583', '0.25',
             '-0.14', '99.86', '57.0', '0.475', '0.725',
             '99.86', '199.86', '29.0', '0.2417', '0.9667',
             '199.86', '299.86', '4.0', '0.0333', '1.0',
             '299.86', '399.86', '0.0', '0.0', '1.0',
             '399.86', '499.86', '0.0', '0.0', '1.0',
             '499.86', '599.86', '0.0', '0.0', '1.0',
             '599.86', '699.86', '0.0', '0.0', '1.0',
             '699.86', '799.86', '0.0', '0.0', '1.0'],
            ['Lower edge', 'Upper edge', 'Absolute', 'Relative', 'Cumulative',
             '-13.5', '-12.5', '1.0', '1.0', '1.0'],
            ['Lower edge', 'Upper edge', 'Absolute', 'Relative', 'Cumulative',
             '-390.0', '-289.4645', '8.0', '0.0667', '0.0667',
             '-289.4645', '-188.929', '8.0', '0.0667', '0.1334',
             '-188.929', '-88.3935', '8.0', '0.0667', '0.2001',
             '-88.3935', '12.142', '38.0', '0.3167', '0.5168',
             '12.142', '112.6775', '29.0', '0.2417', '0.7585',
             '112.6775', '213.213', '29.0', '0.2417', '1.0002'],
            ['Lower edge', 'Upper edge', 'Absolute', 'Relative', 'Cumulative',
             '-300.0', '500.0', '1.0', '1.0', '1.0'],
            ['Lower edge', 'Upper edge', 'Absolute', 'Relative', 'Cumulative',
             '-300.0', '-220.0', '7.0', '0.0583', '0.0583',
             '-220.0', '-140.0', '6.0', '0.05', '0.1083',
             '-140.0', '-60.0', '6.0', '0.05', '0.1583',
             '-60.0', '20.0', '38.0', '0.3167', '0.475',
             '20.0', '100.0', '23.0', '0.1917', '0.6667',
             '100.0', '180.0', '23.0', '0.1917', '0.8584',
             '180.0', '260.0', '10.0', '0.0833', '0.9417',
             '260.0', '340.0', '0.0', '0.0', '0.9417',
             '340.0', '420.0', '0.0', '0.0', '0.9417',
             '420.0', '500.0', '0.0', '0.0', '0.9417']
        ]
        results = app.root.ids.results
        skipone = False  # if top padding with widget present
        for c in reversed(results.children):
            if 'Widget' in str(c):
                skipone = True
                break

        resvals = []
        for i, exp in enumerate(expected):
            i = i + 1 if skipone else i
            # table-like widget
            resgrid = results.children[i].ids.page.children[1].children[1]
            # reverse children order
            children = [child.text for child in reversed(resgrid.children)]
            resvals.extend([children])
        # reverse value order
        resvals = [v for v in reversed(resvals)]
        self.assertEqual(resvals, expected)
        app.stop()

    def test_tasks_basic_freq(self):
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
