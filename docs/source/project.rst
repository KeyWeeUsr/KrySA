.. _project:

Project
=======

.. |charlimit| replace:: can have only lowercase & uppercase ASCII and numbers
.. |crash| replace:: it may result in unexpected behavior and KrySA may crash

As it's obvious from the title, the main part of the application is a
:ref:`project` which is a folder with a ``.krysa`` file and some folders e.g.
for :ref:`data` and :ref:`results`. You are forced to create a :ref:`project`
even with not being able to import data alone. It keeps your work at one place
and makes it simplier to :ref:`osproject` it.

Select ``File -> New -> Project``, navigate to a folder you want to save it to
and KrySA will create a ``<Project name>`` folder there. Project's name
|charlimit|.

.. warning:: Please do not manually edit any of the files, |crash|

.. _osproject:

Open and Save
-------------

Open
~~~~

To open already existing :ref:`project` select ``File -> Open Project`` and
then navigate to a folder with ``.krysa`` file. Select the file with a click or
tap and press ``Open``.

Save
~~~~

Each new :ref:`project` is automatically saved in the beginning with an empty
:ref:`sqlite` and already created folders. Please do not remove any of them even
if it's nothing there.

To save changes made in a new :ref:`project` select ``File -> Save Project``,
it will already know there's an active project and save it in the same folder
without selecting where to save it.

.. note:: If there's no active project, saving does nothing.

.. _sqlite:

Data file
---------

KrySA creates a single ``.sqlite`` file which handles all the :ref:`data` you
create. Although `SQLite` doesn't limit its columns by default, KrySA uses this
option to prevent crashing caused by a user's mistake of running a :ref:`task`
expecting only numbers with a value of type `TEXT`.

.. _data:

Data
~~~~

In the beginning there's an empty :ref:`sqlite`, which means we need to
populate it.

Select ``File -> New -> Data`` and name it. Data's name |charlimit|. Then
create columns (same rules for the names) and input new values to them.
Remember, for each column you have to select a type of its values:

========== ========================================================
   Type    Description
---------- --------------------------------------------------------
REAL       Only numbers with a single ``.`` symbol (``1.1``)
INTEGER    Only numbers without any special symbols
TEXT       Non-limited value converting input directly to unicode
========== ========================================================

.. note:: When an input box for the first value is added, the type of the
   column automatically locks to prevent values of different type in the single
   column e.g. `REAL` and `TEXT`.

.. warning:: Each column must have a unique name!

After the column is finished, you can ``Check & Lock`` the values. It'll check
if the values are the same as the column type and tell you if not. You can
always unlock the values later for example if the application tells you about
wrong values. When you're finished, type ``Run``, it'll run ``Check & Lock``
for each available column. If all the columns pass the test, a new tab after
the :ref:`flow` tab is created and then the application export *every* present
data to the :ref:`sqlite`.

Each column in finished :ref:`data` has an address you can access it later with
in a :ref:`task`.

Importing
~~~~~~~~~

Whenever you want to combine data from two or more :ref:`project` s or just add
additional tables from premade :ref:`sqlite`, this is the way.

Select ``File -> Import Data``, navigate to ``.sqlite`` file, select it with
a click or tap and press ``Import``. It will add another tab(s) containing the
data at the end of the panel.

.. warning:: Before importing check if the column names don't collide,
   otherwise |crash|.

Exporting
~~~~~~~~~

This will export *all* data you can see on the panel to a :ref:`sqlite` which
can be then accessed either with different editor or saved for later use in
KrySA e.g. for combining data.

Select ``File -> Export Data``, navigate to a folder you want to put the
:ref:`sqlite` to, select it with a click or tap and press ``Export``.

.. _results:

Results
-------

Nothing yet.

.. _flow:

Process Flow
------------

Nothing yet.
