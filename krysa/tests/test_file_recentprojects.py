import unittest

import os
import sys
import time
import os.path as op
from shutil import rmtree
from functools import partial
from kivy.clock import Clock

main_path = op.dirname(op.dirname(op.abspath(__file__)))
sys.path.append(main_path)
from main import KrySA


class Test(unittest.TestCase):
    def pause(*args):
        time.sleep(0.000001)

    def run_test(self, app, *args):
        Clock.schedule_interval(self.pause, 0.000001)

        # Run twice, test switching projects on True
        recent_file = op.join(app.user_data_dir, 'recent_projects.krysa')
        for create in range(2):
            if create:
                # Create new project
                app.root._new_project()
                app.root.savedlg.view.selection = [self.folder, ]
                app.root.savedlg.ids.name.text = 'Test.krysa'
                app.root.savedlg.run([self.folder, ], 'Test.krysa')
                project_folder = op.join(self.path, 'test_folder', 'Test')
                data = op.join(project_folder, 'data')
                results = op.join(project_folder, 'results')

                # Write paths
                test_file = op.join(self.path, 'test_Project', 'Test.krysa\n')
                with open(recent_file, 'w') as f:
                    paths = '/just/random/path.krysa\n' * 4 + test_file
                    f.write(paths)

            # Show recent projects
            app.root.recent_projects(app.root)
            self.assertTrue(op.exists(recent_file))
            with open(recent_file) as f:
                lines = f.readlines()

            if create:
                self.assertEqual(len(lines), 5)
            else:
                self.assertEqual(lines, [])

        # Check if correct path and open
        self.assertTrue('test_Project' in lines[-2])
        path = app.root._recent_projects()
        for p in path:
            if 'test_Project' in p:
                path = p
        app.root._open_recent(path)
        app.stop()

    def test_file_recentprojects(self):
        self.path = op.dirname(op.abspath(__file__))
        if not op.exists(op.join(self.path, 'test_folder')):
            os.mkdir(op.join(self.path, 'test_folder'))
        else:
            rmtree(op.join(self.path, 'test_folder'))
            os.mkdir(op.join(self.path, 'test_folder'))
        self.folder = op.join(self.path, 'test_folder')

        app = KrySA()
        rmtree(app.user_data_dir)
        p = partial(self.run_test, app)
        Clock.schedule_once(p, .000001)
        app.run()
        rmtree(app.user_data_dir)
        rmtree(self.folder)


if __name__ == '__main__':
    unittest.main()
