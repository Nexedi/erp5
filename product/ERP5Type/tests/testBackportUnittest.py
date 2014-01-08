# Tester
import unittest

# Implementation being tested
from backportUnittest import TestCase, TextTestRunner, skip, expectedFailure

class TestBackportUnittest(unittest.TestCase):
  def setUp(self):
    self.stream = open('/dev/null', 'w')
    self.runner = TextTestRunner(self.stream)

  def testSuccessfulTest(self):
    class Success(TestCase):
      def runTest(self):
        self.assert_(True)

    test_instance = Success()
    result = self.runner.run(test_instance)

    self.assertEqual(result.testsRun, 1)
    self.assertEqual(len(result.errors), 0)
    self.assertEqual(len(result.failures), 0)
    self.assertEqual(len(result.expectedFailures), 0)
    self.assertEqual(len(result.unexpectedSuccesses), 0)
    self.assertEqual(len(result.skipped), 0)

    self.assert_(result.wasSuccessful())

  def testFailingTest(self):
    class Failure(TestCase):
      def runTest(self):
        self.assert_(False)

    test_instance = Failure()
    result = self.runner.run(test_instance)

    self.assertEqual(result.testsRun, 1)
    self.assertEqual(len(result.errors), 0)
    self.assertEqual(len(result.failures), 1)
    self.assertEqual(len(result.expectedFailures), 0)
    self.assertEqual(len(result.unexpectedSuccesses), 0)
    self.assertEqual(len(result.skipped), 0)

    self.assert_(not result.wasSuccessful())

  def testSkippingUsingMethodDecorator(self):
    class Skipped(TestCase):
      @skip("Hey, let's skip this!")
      def runTest(self):
        self.assert_(False)

    test_instance = Skipped()
    result = self.runner.run(test_instance)

    self.assertEqual(result.testsRun, 1)
    self.assertEqual(len(result.errors), 0)
    self.assertEqual(len(result.failures), 0)
    self.assertEqual(len(result.expectedFailures), 0)
    self.assertEqual(len(result.unexpectedSuccesses), 0)
    self.assertEqual(len(result.skipped), 1)

    self.assert_(result.wasSuccessful())

  def testSkippingUsingClassDecorator(self):
    class Skipped(TestCase):
      def runTest(self):
        self.assert_(False)

    Skipped = skip("Class Skip?")(Skipped)

    test_instance = Skipped()
    result = self.runner.run(test_instance)

    self.assertEqual(result.testsRun, 1)
    self.assertEqual(len(result.errors), 0)
    self.assertEqual(len(result.failures), 0)
    self.assertEqual(len(result.expectedFailures), 0)
    self.assertEqual(len(result.unexpectedSuccesses), 0)
    self.assertEqual(len(result.skipped), 1)

    self.assert_(result.wasSuccessful())

  def testSkippingUsingSkipTest(self):
    class Skipped(TestCase):
      def runTest(self):
        self.skipTest("Hey, let's skip this test!")
        self.assert_(False)

    test_instance = Skipped()
    result = self.runner.run(test_instance)

    self.assertEqual(result.testsRun, 1)
    self.assertEqual(len(result.errors), 0)
    self.assertEqual(len(result.failures), 0)
    self.assertEqual(len(result.expectedFailures), 0)
    self.assertEqual(len(result.unexpectedSuccesses), 0)
    self.assertEqual(len(result.skipped), 1)

    self.assert_(result.wasSuccessful())

  def testExpectedFailure(self):
    class WillFail(TestCase):
      @expectedFailure
      def runTest(self):
        self.assert_(False)

    test_instance = WillFail()
    result = self.runner.run(test_instance)

    self.assertEqual(result.testsRun, 1)
    self.assertEqual(len(result.errors), 0)
    self.assertEqual(len(result.failures), 0)
    self.assertEqual(len(result.expectedFailures), 1)
    self.assertEqual(len(result.unexpectedSuccesses), 0)
    self.assertEqual(len(result.skipped), 0)

    self.assert_(result.wasSuccessful())

  def testUnExpectedSuccess(self):
    class WillNotFail(TestCase):
      @expectedFailure
      def runTest(self):
        self.assert_(True)

    test_instance = WillNotFail()
    result = self.runner.run(test_instance)

    self.assertEqual(result.testsRun, 1)
    self.assertEqual(len(result.errors), 0)
    self.assertEqual(len(result.failures), 0)
    self.assertEqual(len(result.expectedFailures), 0)
    self.assertEqual(len(result.unexpectedSuccesses), 1)
    self.assertEqual(len(result.skipped), 0)

    # Unexpected success does not FAIL the test
    self.assert_(not result.wasSuccessful())

if __name__ == "__main__":
  unittest.main()
