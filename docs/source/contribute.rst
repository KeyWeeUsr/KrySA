.. _contribute:

Contributing
============

There are three parts of the project you can contribute to, but only two of
them require at least some programming skills (mainly in Python). Each part,
however, requires a fully functional KrySA application.

.. |suite| replace:: Test Suite
.. _suite: https://github.com/KeyWeeUsr/KrySA/tests

Documentation
-------------

.. |rst| replace:: reStructuredText
.. _rst: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html
.. |format| replace:: (max 79 characters in a single line)

As the project is still in the beginning, there's a lot of things to document
and to make screenshots of. If you have KrySA already installed, there's a
``docs`` folder that contains the documentation.

The documentation is written in |rst|_ which you can test either in some online
editor (referencing files won't work, obviously) or localy if you have already
installed Python. KrySA uses `Sphinx <https://sphinx-doc.org>`_ for converting
|rst| to a html website. First install requirements from the ``.txt`` file. ::

    pip install -r docs-requirements.txt

To build the documentation use these commands in the ``docs`` folder::

    make clean && make html

.. note:: Extend the command with another ``&&`` to e.g. automatically open a
   browser with fresh ``index.html`` file.

Please don't break the formatting |format| and fix the errors if any jumps out
in Sphinx build.

Statistics
----------

Hypotesis testing, factor analysis, averages, whatever part of statistics you
think a user could find useful you can do two things:

#. Feature request

   Open an issue in the GitHub repository describing the feature and its
   use case.

#. Pull request

   Read the code, find out how it works and make a pull request to the GitHub
   repository with code that doesn't break the |suite|_ together with an
   example of how the new feature works.

Application
-----------

.. |kut| replace:: KivyUnitTest
.. _kut: https://github.com/KeyWeeUsr/KivyUnitTest
.. |pep8| replace:: PEP8 style
.. _pep8: https://pypi.python.org/pypi/pep8

If you think the application might find your feature useful or that some
behavior needs a fix, you are welcome to make a pull request. Before each pull
make sure it is written in Python's |pep8|_ and that it doesn't break the
|suite|_. |kut|_ makes running the tests easier.
