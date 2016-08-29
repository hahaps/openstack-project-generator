=====================================
OpenStack <Project_name> Testing Infrastructure
=====================================

A note of clarification is in order, to help those who are new to testing in
OpenStack <project_name>:

- actual unit tests are created in the "tests" directory;
- the "testing" directory is used to house the infrastructure needed to support
  testing in OpenStack <Project_name>.

This README file attempts to provide current and prospective contributors with
everything they need to know in order to start creating unit tests and
utilizing the convenience code provided in <project_name>.testing.

For more detailed information on <project_name> unit tests visit:
http://docs.openstack.org/developer/<project_name>/devref/unit_tests.html

Running Tests
-----------------------------------------------

In the root of the <project_name> source code run the run_tests.sh script. This will
offer to create a virtual environment and populate it with dependencies.
If you don't have dependencies installed that are needed for compiling <project_name>'s
direct dependencies, you'll have to use your operating system's method of
installing extra dependencies. To get help using this script execute it with
the -h parameter to get options `./run_tests.sh -h`

Writing Unit Tests
------------------

- All new unit tests are to be written in python-mock.
- Old tests that are still written in mox should be updated to use python-mock.
    Usage of mox has been deprecated for writing <Project_name> unit tests.
- use addCleanup in favor of tearDown
