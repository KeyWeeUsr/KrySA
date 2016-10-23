# -*- coding: utf-8 -*-
import os
import sys
import os.path as op

print('Creating modules from {}'.format(op.basename(__file__)))
include_exts = ('.py',)
exclude_dirs = ('test_Project',)
exclude_files = ('dropdown.py', '__main__.py', 'test_file_', 'test_tasks_')

mod_sep = u' » '

paths = []
rootdir = op.join(op.dirname(op.dirname(op.abspath(__file__))), 'krysa')
sourcedir = op.join(op.dirname(op.abspath(__file__)), 'source')

print('Getting paths...')
for path, folders, files in os.walk(rootdir):
    dirname = op.basename(path)
    for ex in exclude_dirs:
        if ex not in path:
            sys.path.insert(0, path)
            paths.append(path)

print('Getting files... {}'.format(include_exts))
docs = []
for p in paths:
    for path, folders, files in os.walk(p):
        for f in files:
            if op.splitext(f)[1] in include_exts:
                docs.append(op.join(op.basename(path), f))

for doc in docs:
    for ex in exclude_files:
        docs = [d for d in docs if ex not in d]

print('Filtering files...')
mods = []
for doc in docs:
    mod = doc.lstrip('krysa' + op.sep).replace(op.sep, '.')
    mod = mod.replace('__init__.py', '')
    if not mod:
        continue
    if mod[-1] == '.':
        mod = mod[:-1]
    mod = op.splitext(mod)[0]
    if 'main' not in mod:
        name = 'KrySA' + mod_sep
        if '.' in mod:
            name += mod.replace('.', mod_sep).title()
        else:
            name += mod.title()
    else:
        name = 'KrySA'
    if (name, mod) not in mods:
        mods.append((name, mod))

print('Writing output...')
for mod in mods:
    mod_name = mod[0].replace(mod_sep, '_').lower()
    with open(op.join(sourcedir, 'mod_{}.rst'.format(mod_name)), 'w') as f:
        f.write('{}\n'.format(mod[0].encode('utf-8')))
        f.write('=' * len(mod[0]))
        f.write('\n\n.. automodule:: {}\n'.format(mod[1]))
        f.write('   :members:')

with open(op.join(sourcedir, 'mod_index.rst'), 'w') as f:
    f.write('Modules\n')
    f.write('=======\n\n')
    f.write('* `Index <py-modindex.html>`_\n\n')
    f.write('.. toctree::\n')
    f.write('   mod_krysa\n')
    f.write('   mod_krysa_tasks\n')
    f.write('   mod_krysa_utils\n')
    f.write('   mod_krysa_tests\n')

print('Full docs done...')
