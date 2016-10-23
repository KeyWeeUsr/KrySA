'''
A bunch of useful functions separated from the source.
'''

from kivy.utils import platform
from functools import partial
import subprocess
import webbrowser
import os

# probably only the first two will be in KrySA
image_ext = ['.png', '.jpg', '.gif', '.tiff']


# linux & mac need testing
def create_bind(path):
    '''Creates a partial for opening a file in system's default program
    for such file extensions.

    .. versionadded:: 0.5.0
    '''
    if isimage(path):
        if platform == 'macosx':
            return partial(subprocess.call, ('open', path))
        elif platform == 'win':
            return partial(win_system, '"' + path + '"')
        elif platform == 'linux':
            return partial(subprocess.call, ('xdg-open', path))
    else:
        return partial(webbrowser.open, path)


def win_system(arg, *args):
    # just a wrapper, because it threw
    # an error about too many args
    os.system(arg)


def isimage(image):
    '''Compares a file from path with the explicitly listed extensions
    for images, such as `.png`.

    :Returns:
       `boolean`

    .. versionadded:: 0.5.0
    '''
    global image_ext

    if platform in ['android', 'ios', 'unknown']:
        return None

    for ext in image_ext:
        if ext in image:
            return True
