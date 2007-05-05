#!/usr/bin/env python

from indentphp import indentfile
import unittest
from glob import glob
from commands import getoutput, mkarg
from os import unlink

class TestIndentPHP(unittest.TestCase):
    def testall(self):
        files = glob('tests/???-*.php')
        files.sort()
        for infilename in files:
            outfilename = 'tests/out%s' % infilename[5:]
            expectedfilename = 'tests/expected%s' % infilename[5:]

            indentfile(infilename, outfilename)
            output = getoutput('LC_ALL=C diff -u %s %s' % (mkarg(outfilename),  
                                                 mkarg(expectedfilename)))

            unlink(outfilename)
            self.assertEqual(output, '', "\n" + output)

            indentfile(expectedfilename, outfilename)
            output = getoutput('LC_ALL=C diff -u %s %s' % (mkarg(outfilename),  
                                                 mkarg(expectedfilename)))
            unlink(outfilename)
            self.assertEqual(output, '', "\n" + output)



if __name__ == '__main__':
    unittest.main()
