Getting started
===============

.. warning:: KrySA is still in pre-alpha, most of the features are buggy or not
   yet supported. Read :ref:`contribute` section if you want to help speed up
   the process.

KrySA runs on Kivy framework, therefore it is possible to run it on any of
available platforms for Kivy, mainly Windows, Linux and Mac. It requires some
additional packages you'll need to install if you want to run it:

- `Kivy <https://kivy.org>`_
- `SciPy <https://scipy.org>`_
- `NumPy <https://numpy.org>`_
- `MatPlotLib <https://matplotlib.org>`_

There's no executable for KrySA yet, you'll need to install it from source and
run with Python until there is a release available. Don't worry, it'll be
explained later.

Minimum system requirements
---------------------------

=============== ========================================================
RAM             At least 256 MB
Disk space      At least 400 MB free
Resolution      Minimum of 800 x 600
CPU             ? ? ?
GPU             Anything with OpenGL 2.0 support should be enough
Internet        Necessary for downloading requirements and updating
=============== ========================================================

Installation
------------

.. |nspywhl| replace:: here
.. _nspywhl: http://localhost
.. |kivyinstall| replace:: Kivy Installation
.. _kivyinstall: https://kivy.org/docs/installation/installation.html

First of all you'll need `Python <https://python.org>`_. To simplify the
process use `KivyInstaller <https://github.com/KeyWeeUsr/KivyInstaller>`_ on
Windows, which will install Python together with Kivy. On other platforms use
|kivyinstall|_ page as reference.

.. note:: KrySA requires the latest version of Kivy. It's available either as
   daily-builds on ``ppa`` or as a ``.whl`` files uploaded on Google Drive. If
   none of those are good, compile Kivy from source.

Then it gets a little bit harder with SciPy and NumPy because those need to be
compiled and it doesn't work with Windows really good. For this case we will
use already compiled packages in ``.whl`` files. You can find them |nspywhl|_.
Choose packages for Python 2.7 (cp27). On Linux they should work without issues
with ``pip install <package>``. ::

    pip install <path to package>.whl

Then install MatPlotLib. This is easy even on Windows::

    pip install matplotlib

Getting KrySA
-------------

There are many ways how to get it, but basically you need to download it from
the `official repository <https://github.com/KeyWeeUsr/KrySA>`_.

#. Git

   Clone the whole repository and be able to update KrySA when a new version
   arrives with a simple ``git pull``. ::

        git clone https://github.com/KeyWeeUsr/KrySA

#. Zip

   Click on the ``Clone or download`` button, download the zip file and unpack
   its contents.

When the folder with KrySA is ready, simply navigate into it and run::

    python main.py
