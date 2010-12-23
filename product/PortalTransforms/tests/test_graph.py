from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase

from utils import input_file_path
FILE_PATH = input_file_path("demo1.pdf")

class TestGraph(ATSiteTestCase):

    def afterSetUp(self):
        ATSiteTestCase.afterSetUp(self)
        self.engine = self.portal.portal_transforms

    def testGraph(self):
        data = open(FILE_PATH, 'r').read()
        requirements = self.engine._policies.get('text/plain', [])
        if requirements:
            out = self.engine.convertTo('text/plain', data, filename=FILE_PATH)
            self.failUnless(out.getData())

    def testFindPath(self):
        originalMap = self.engine._mtmap
        """
        The dummy map used for this test corresponds to a graph
        depicted in ASCII art below :
        
        +---+
        |   |
        |   v
        +-->1<-->2-->4-->6<--7
            ^    ^   |
            |    |   |
            v    |   |
            3<---+   |
            ^        |
            |        |
            v        |
            5<-------+
        """
        # we need a DummyTransform class
        class DT:
            def __init__(self, name):
                self._name = name
            def name(self):
                return self._name
        
        dummyMap1 = {
            '1': { '1': [DT('transform1-1')],
                   '2': [DT('transform1-2')],
                   '3': [DT('transform1-3')]},
            '2': { '1': [DT('transform2-1')],
                   '3': [DT('transform2-3')],
                   '4': [DT('transform2-4')]},
            '3': { '1': [DT('transform3-1')],
                   '2': [DT('transform3-2')],
                   '5': [DT('transform3-5')]},
            '4': { '5': [DT('transform4-5')],
                   '6': [DT('transform4-6')]},
            '5': { '3': [DT('transform5-3')]},
            '7': { '6': [DT('transform7-6')]}
        }
        expectedPathes = {
            '1-1': [],
            '1-2': ['transform1-2'],
            '1-3': ['transform1-3'],
            '1-4': ['transform1-2', 'transform2-4'],
            '1-5': ['transform1-3', 'transform3-5'],
            '1-6': ['transform1-2', 'transform2-4', 'transform4-6'],
            '1-7': None,
            '2-1': ['transform2-1'],
            '2-2': [],
            '2-4': ['transform2-4'],
            '4-2': ['transform4-5', 'transform5-3', 'transform3-2'],
            '5-3': ['transform5-3']
        }
        self.engine._mtmap = dummyMap1
        for orig in ['1','2','3','4','5','6','7']:
            for target in ['1','2','3','4','5','6','7']:
                # build the name of the path
                pathName = orig + '-' + target
                # do we have any expectation for this path ?
                if pathName in expectedPathes.keys():
                    # we do. Here is the expected shortest path
                    expectedPath = expectedPathes[pathName]
                    # what's the shortest path according to the engine ?
                    gotPath = self.engine._findPath(orig,target)
                    # just keep the name of the transforms, please
                    if gotPath is not None:
                        gotPath = [transform.name() for transform in gotPath]
                    # this must be the same as in our expectation
                    self.assertEquals(expectedPath, gotPath)
        self.engine._mtmap = originalMap

    def testFindPathWithEmptyTransform(self):
        """ _findPath should not throw "index out of range" when dealing with
            empty transforms list
        """
        dummyMap = {'1': {'2': []}}
        self.engine._mtmap = dummyMap
        self.engine._findPath('1','2')
    
    def testIdentity(self):
        orig = 'Some text'
        converted = self.engine.convertTo(
            'text/plain', 'Some text', mimetype='text/plain')
        self.assertEquals(orig, str(converted))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGraph))
    return suite
