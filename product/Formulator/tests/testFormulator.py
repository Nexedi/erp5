# -*- coding: utf-8 -*-
# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $
import unittest
import Zope2

try:
    from Zope2 import startup
    startup()
except ImportError:
    # startup is only in Zope2.6
    pass

from Products.Formulator.tests import testForm, testFormValidator, testSerializeForm

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(testForm.test_suite())
    suite.addTest(testFormValidator.test_suite())
    suite.addTest(testSerializeForm.test_suite())
    return suite

def main():
    unittest.TextTestRunner(verbosity=1).run(test_suite())

if __name__ == '__main__':
    main()
