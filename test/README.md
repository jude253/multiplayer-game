# Overview

This directory contains tests for the code in this module.  This may not
be the best way to configure the tests, but for now, this way works.
Wondering if the coverage metrics will show up correctly for python
packages if the tests for the package is not in the same BUILD file?

This way of packaging is easier so that I don't have to remove the test
directory from with a python packages or add anothe subpackge within
each subpackage such as maybe `src/pkg_name` so that I can leave the
tests out of the exported/imported libary or package.
