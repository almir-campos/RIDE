#!/usr/bin/env python

"""Helper script to run all Robot Framework's unit tests.

usage: run_utest.py [options]

options: 
    -q, --quiet     Minimal output
    -v, --verbose   Verbose output
    -d, --doc       Show test's doc string instead of name and class
                    (implies verbosity)
    -h, --help      Show help
"""

import unittest
import os
import sys
import re
import getopt

base = os.path.abspath(os.path.dirname(__file__))
for path in [ "../src"]:
    path = os.path.join(base, path.replace('/', os.sep))
    if path not in sys.path:
        sys.path.insert(0, path)

testfile = re.compile("^test_.*\.py$", re.IGNORECASE)

loaded_modules = []


def get_tests(patterns, directory=None):
    if directory is None:
        directory = base
    sys.path.append(directory)
    tests = []
    modules = []
    for name in os.listdir(directory):
        if name.startswith("."): continue
        fullname = os.path.join(directory, name)
        if os.path.isdir(fullname):
            tests.extend(get_tests(patterns, fullname))
        elif testfile.match(name) and _match_pattern(name, patterns):
            modules.append(_get_module(directory, name))
    tests.extend([ unittest.defaultTestLoader.loadTestsFromModule(module)
                   for module in modules ])
    return tests


def _get_module(directory, name):
    modname = os.path.splitext(name)[0]
    if modname in loaded_modules:
        msg = "Cannot run module '%s' from '%s' as module with same name " +\
        "already exists. Please rename your module."
        raise RuntimeError(msg % (modname, directory))
    loaded_modules.append(modname) 
    return __import__(modname)


def _match_pattern(name, patterns):
    if not patterns:
        return True
    for pattern in patterns:
        if pattern in name:
            return True
    return False


def parse_args(argv):
    docs = 0
    verbosity = 1
    args = []
    try:
        options, args = getopt.getopt(argv, 'hH?vqd', 
                                      ['help','verbose','quiet','doc'])
    except getopt.error, err:
        usage_exit(err)
    for opt, _ in options:
        if opt in ('-h','-H','-?','--help'):
            usage_exit()
        if opt in ('-q','--quit'):
            verbosity = 0
        if opt in ('-v', '--verbose'):
            verbosity = 2
        if opt in ('-d', '--doc'):
            docs = 1
            verbosity = 2
    return docs, verbosity, args


def usage_exit(msg=None):
    print __doc__
    if msg is not None: 
        print '\nError:', msg
    sys.exit(2)


if __name__ == '__main__':
    docs, vrbst, patterns = parse_args(sys.argv[1:])
    tests = get_tests(patterns)
    suite = unittest.TestSuite(tests)
    runner = unittest.TextTestRunner(descriptions=docs, verbosity=vrbst)
    result = runner.run(suite)
    if len(result.failures) + len(result.errors) > 0 :
        sys.exit(1)
    sys.exit()
