#!/usr/bin/env python
#
# Copyright 2006 David Anderson <david.anderson@calixo.net>
#                Ben Collins-Sussman <sussman@red-bean.com>
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.

from unittest import defaultTestLoader as loader, \
     TextTestRunner as runner
from sys import argv
import tests

if len(argv) > 1:
    suite = loader.loadTestsFromNames(["tests.%s_tests" % s
                                       for s in argv[1:]])
else:
    suite = loader.loadTestsFromNames(["tests.%s" % s
                                       for s in tests.__all__])

runner().run(suite)
