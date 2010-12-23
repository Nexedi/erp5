import unittest
from zope.testing import doctestunit

modules = (
    'Products.PortalTransforms.transforms.rest',
    )

def test_suite():
    return unittest.TestSuite(
        [doctestunit.DocTestSuite(module=module) for module in modules]
        )
