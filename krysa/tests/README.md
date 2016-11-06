# Tests

Tests need to run independently on each other, not in a single python
interpreter. After each test a fresh `python` is required, so either run them
like this one by one:

    python test_<something>.py

or use [KivyUnitTest](https://github.com/KeyWeeUsr/KivyUnitTest) to do it
instead of you.

To test if your installation works properly, navigate to Python's
`site-package` folder and run the tests with:

    python -m kivyunittest --folder "krysa/tests"
