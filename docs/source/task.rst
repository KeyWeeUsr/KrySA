.. _task:

Task
====

This is the most important part of KrySA, it is the way of manipulating
:ref:`data` values and reporting the result. Tasks are categorized by its
purpose and/or complexity into different groups e.g. ``Basic``.

.. _usingtask:

Using a Task
------------

Each :ref:`task` needs values which it can use, otherwise it won't run. When
the values are present, each column has an address starting with ``A`` for the
first column. To select more than a single value, use ``:`` character e.g.
``B1:AB2``:

= = = = === == == == === =====
. A B C ... AA AB AC ... ZZ...
1   x x  x  x  x
2   x x  x  x  x
= = = = === == == == === =====

After the values are selected, pres ``Run``. Depending on the :ref:`task`, it
can create new :ref:`data` or a page in the :ref:`results` panel.

.. _createtask:

Create a Task
-------------

Since KrySA uses Python, each :ref:`task` begins with a function named like
this::

    def <category>_<task>(self, *args):

This function sets the layout that is put into the :ref:`task` popup, sets a
function that is called when user selects some options in the popup and opens
it. The :ref:`task` s layout contains an option to select which :ref:`data`
will be used in the following task, but you have to handle user's input of the
address(``A1:B2``). ::

    def <category>_<task>(self, *args):
        widget = SomeLayout()
        task = Task(title='Title', wdg=widget,
                    call=['Title', self.<category>_<task>])
        task.run = partial(self.<called function>,
                           task,
                           <widget containing address>)

It's necessary to put into ``Task()`` the layout and a link to itself. Layout
then can be accessed in the called function directly from arguments and the
link is used to append the used :ref:`task` to list of `Recent Tasks`.

Then it's necessary to write the ``<called function>`` and handle its inputs.
Each :ref:`task` must have some kind of output - new :ref:`data`, modified
:ref:`data` or a page in the :ref:`results`. ::

    def <called_function>(self, task, address, *args):

Each ``<called function>`` takes at least two arguments ``task`` and
``address``, where ``task`` is the main popup (so that you can access the
chosen :ref:`data`) and ``address`` is the widget with ``text`` property.

To get the values from user's input use the function `Body.from_address()` ::

    values = self.from_address(task.tablenum, address.text)

When you are finished, output the values e.g. into :ref:`results`::

    self.set_page('Count', str(len(values)), 'text')

Final function would look like this::

    def _basic_count(self, task, address, *args):
        values = self.from_address(task.tablenum, address.text)
        self.set_page('Count', str(len(values)), 'text')
