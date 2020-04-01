##############################################################################
#
# Copyright (c) 2017 Nexedi KK and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import os.path
import tempfile
import textwrap
import unittest
import uuid

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Type.tests.utils import removeZODBPythonScript
from Products.ERP5Type.patches.Restricted import allow_class_attribute
from AccessControl import Unauthorized


class TestRestrictedPythonSecurity(ERP5TypeTestCase):
  """
    Test Restricted Python Security that is monkey patched by ERP5.
  """

  def getTitle(self):
    return "Restricted Python Security Test"

  def runScript(self, container, name, kwargs):
    func = getattr(self.portal, name)
    return func(**kwargs)

  def createAndRunScript(self, *args, **kwargs):
    # we do not care the script name for security test thus use uuid1
    name = str(uuid.uuid1())
    code = '\n'.join(args)
    expected = kwargs.get('expected', None)
    script_container = self.portal.portal_skins.custom
    try:
      createZODBPythonScript(script_container, name, '**kw', code)
      if expected:
        self.assertEqual(self.runScript(script_container, name, kwargs.get('kwargs', {})), expected)
      else:
        self.runScript(script_container, name, kwargs.get('kwargs', {}))
    finally:
      removeZODBPythonScript(script_container, name)

  def testDateTimeModuleAllowance(self):
    """
      Make sure the security configuration with creating the Python(Script),
      and running the Script.
    """
    self.createAndRunScript('import datetime')
    self.createAndRunScript('import datetime', 'return datetime.datetime.now()')
    self.createAndRunScript('import datetime', 'return datetime.time.max')
    self.createAndRunScript('import datetime', 'return datetime.date.today()')
    self.createAndRunScript('import datetime', 'return datetime.timedelta.min')
    self.createAndRunScript('import datetime', 'return datetime.tzinfo')
    self.createAndRunScript('import datetime',
                            "return datetime.datetime.strptime('', '')")

  def testDictClassMethod(self):
    # This is intended to be allowed from the beggining
    self.createAndRunScript("return dict.fromkeys(['a', 'b', 'c'])")

  def testDecimalClassMethod(self):
    # Now it is not allowed
    self.assertRaises(Unauthorized,
      self.createAndRunScript, 'import decimal',
                               'return decimal.Decimal.from_float(3.3)')
    # allow it only in this test class to check
    import decimal
    allow_class_attribute(decimal.Decimal, {"from_float":1})
    # make sure now we can run without raising Unauthorized
    self.createAndRunScript('import decimal',
                            'return decimal.Decimal.from_float(3.3)')

  def test_urlparse(self):
    self.createAndRunScript(
        'import urlparse',
        'return urlparse.urlparse("http://example.com/pa/th/?q=s").path',
        expected='/pa/th/'
    )
    # access computed attributes (property) is also OK
    self.createAndRunScript(
        'import urlparse',
        'return urlparse.urlparse("http://example.com/pa/th/?q=s").hostname',
        expected='example.com'
    )
    self.createAndRunScript(
        'import urlparse',
        'return urlparse.urlsplit("http://example.com/pa/th/?q=s").path',
        expected='/pa/th/'
    )
    self.createAndRunScript(
        'import urlparse',
        'return urlparse.urldefrag("http://example.com/#frag")[1]',
        expected='frag'
    )
    self.createAndRunScript(
        'import urlparse',
        'return urlparse.parse_qs("q=s")',
        expected={'q': ['s']}
    )
    self.createAndRunScript(
        'import urlparse',
        'return urlparse.parse_qsl("q=s")',
        expected=[('q', 's')]
    )

  def testSystemRandom(self):
    self.createAndRunScript('import random',
                            'return random.SystemRandom().getrandbits(10)')

  def test_os_urandom(self):
    self.createAndRunScript('import os',
                            'return os.urandom(10)')
    # other "unsafe" os members are not exposed
    self.assertRaises(Unauthorized,
      self.createAndRunScript, 'import os',
                               'return os.path.exists("/")')
    self.assertRaises(Unauthorized,
      self.createAndRunScript, 'import os',
                               'return os.system')
    self.assertRaises(Unauthorized,
      self.createAndRunScript, 'from os import system')

  def test_set(self):
    self.createAndRunScript(
        textwrap.dedent('''\
          s = set()
          s.add(1)
          s.clear()
          s.copy()
          s = set([1, 2])
          s.difference([1])
          s.difference_update([1])
          s.discard(1)
          s.intersection([1])
          s.intersection_update([1])
          s.isdisjoint([1])
          s.issubset([1])
          s.issuperset([1])
          s.add(1)
          s.pop()
          s.add(1)
          s.remove(1)
          s.symmetric_difference([1])
          s.symmetric_difference_update([1])
          s.union([1])
          s.update()
        '''),
    )

  def test_frozenset(self):
    self.createAndRunScript(
        textwrap.dedent('''\
          s = frozenset([1, 2])
          s.copy()
          s.difference([1])
          s.intersection([1])
          s.isdisjoint([1])
          s.issubset([1])
          s.issuperset([1])
          s.symmetric_difference([1])
          s.union([1])
        '''),
    )

  def test_sorted(self):
    self.createAndRunScript(
        textwrap.dedent('''\
          returned = []
          for i in sorted([2, 3, 1]):
            returned.append(i)
          return returned
        '''),
        expected=[1, 2, 3],
    )

  def test_reversed(self):
    self.createAndRunScript(
        textwrap.dedent('''\
          returned = []
          for i in reversed(('3', '2', '1')):
            returned.append(i)
          return returned
        '''),
        expected=['1', '2', '3'],
    )
    self.createAndRunScript(
        textwrap.dedent('''\
          returned = []
          for i in reversed([3, 2, 1]):
            returned.append(i)
          return returned
        '''),
        expected=[1, 2, 3],
    )
    self.createAndRunScript(
        textwrap.dedent('''\
          returned = []
          for i in reversed('321'):
            returned.append(i)
          return returned
        '''),
        expected=['1', '2', '3'],
    )

  def test_enumerate(self):
    self.createAndRunScript(
        textwrap.dedent('''\
          returned = []
          for i in enumerate(["zero", "one", "two",]):
            returned.append(i)
          return returned
        '''),
        expected=[(0, "zero"), (1, "one"), (2, "two"), ],
    )
    # with start= argument
    self.createAndRunScript(
        textwrap.dedent('''\
          returned = []
          for i in enumerate(["one", "two", "three"], start=1):
            returned.append(i)
          return returned
        '''),
        expected=[(1, "one"), (2, "two"), (3, "three")],
    )

  def test_generator_iteration(self):
    generator_iteration_script = textwrap.dedent(
        '''\
        result = []
        for elem in kw['generator']:
          result.append(elem)
        return result
        ''')

    class AllowedObject:
      __allow_access_to_unprotected_subobjects__ = 1
    allowed_object = AllowedObject()

    class NotAllowedObject:
      __roles__ = ()
    not_allowed_object = NotAllowedObject()

    def generator_with_allowed_objects():
      yield 1
      yield "two"
      yield allowed_object

    self.createAndRunScript(
        generator_iteration_script,
        kwargs={'generator': generator_with_allowed_objects()},
        expected=[1, "two", allowed_object],
    )
    # generator expression
    self.createAndRunScript(
        generator_iteration_script,
        kwargs={'generator': (x for x in [1, "two", allowed_object])},
        expected=[1, "two", allowed_object],
    )

    def generator_with_not_allowed_objects():
      yield "one"
      yield not_allowed_object
      yield 2
    self.assertRaises(
        Unauthorized,
        self.createAndRunScript,
        generator_iteration_script,
        kwargs={'generator': generator_with_not_allowed_objects()},
    )

    self.createAndRunScript(
        textwrap.dedent('''\
          result = []
          i = iter(kw['generator'])
          for _ in range(100): # prevent infinite loop
            try:
              result.append(next(i))
            except StopIteration:
              break
            except Exception as e:
              result.append(repr(e))
          return result
        '''),
        kwargs={'generator': generator_with_not_allowed_objects()},
        expected=["one", "Unauthorized()", 2],
    )

  def test_json(self):
    self.createAndRunScript(
        textwrap.dedent('''\
          import json
          return json.loads(json.dumps({"ok": [True]}))
          '''),
        expected={"ok": [True]}
    )

  def test_calendar(self):
    self.createAndRunScript(
        textwrap.dedent('''\
          import calendar
          calendar.IllegalMonthError
          calendar.IllegalWeekdayError
          calendar.calendar(2020)
          calendar.firstweekday()
          calendar.isleap(2020)
          calendar.leapdays(200, 2020)
          calendar.month(2020, 1)
          calendar.monthcalendar(2020, 1)
          calendar.monthrange(2020, 1)
          calendar.setfirstweekday(1)
          calendar.timegm((2020, 1, 1, 0, 0, 0))
          calendar.weekday(2020, 1, 1)
          calendar.Calendar().getfirstweekday()
          calendar.HTMLCalendar().getfirstweekday()
          '''),
    )

  def test_collections_Counter(self):
    self.createAndRunScript(
        textwrap.dedent('''\
          from collections import Counter
          c = Counter(["a", "b"])
          c["a"] = c["a"] + 1
          del c["b"]
          c.update({"a": 1})
          return c.most_common(1)
        '''),
        expected=[('a', 3)]
    )

  def test_collections_defaultdict(self):
    self.createAndRunScript(
        textwrap.dedent('''\
          from collections import defaultdict
          d = defaultdict(list)
          d["x"].append(1)
          d["y"] = 2
          del d["y"]
          return d
          '''),
        expected={"x": [1]}
    )

  def test_collections_namedtuple(self):
    self.createAndRunScript(
        textwrap.dedent('''\
          from collections import namedtuple
          Object = namedtuple("Object", ["a", "b", "c"])
          return Object(a=1, b=2, c=3).a
          '''),
        expected=1
    )
    # also make sure we can iterate on nametuples
    self.createAndRunScript(
        textwrap.dedent('''\
          from collections import namedtuple
          Object = namedtuple("Object", ["a", "b", "c"])
          returned = []
          for x in Object(a=1, b=2, c=3):
            returned.append(x)
          return returned
          '''),
        expected=[1, 2, 3]
    )

  def test_collections_OrderedDict(self):
    self.createAndRunScript(
        textwrap.dedent('''\
          from collections import OrderedDict
          d = OrderedDict()
          d["a"] = 1
          d["b"] = 2
          d["c"] = 3
          del d["c"]
          return list(d.items())
          '''),
        expected=[("a", 1), ("b", 2)]
    )


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestRestrictedPythonSecurity))

  # Also run original tests of RestrictedPython, to confirm that our patches did not break
  # original functionality
  import RestrictedPython.tests.testCompile
  suite.addTest(RestrictedPython.tests.testCompile.test_suite())
  import RestrictedPython.tests.testUtiliities
  suite.addTest(RestrictedPython.tests.testUtiliities.test_suite())
  import RestrictedPython.tests.testREADME
  suite.addTest(RestrictedPython.tests.testREADME.test_suite())
  import RestrictedPython.tests.testRestrictions
  suite.addTest(RestrictedPython.tests.testRestrictions.test_suite())

  import AccessControl.tests.test_requestmethod
  suite.addTest(AccessControl.tests.test_requestmethod.test_suite())
  import AccessControl.tests.test_safeiter
  suite.addTest(AccessControl.tests.test_safeiter.test_suite())
  import AccessControl.tests.test_tainted
  suite.addTest(AccessControl.tests.test_tainted.test_suite())
  import AccessControl.tests.test_formatter
  suite.addTest(unittest.makeSuite(AccessControl.tests.test_formatter.FormatterTest))
  import AccessControl.tests.test_userfolder
  suite.addTest(AccessControl.tests.test_userfolder.test_suite())
  import AccessControl.tests.test_users
  suite.addTest(AccessControl.tests.test_users.test_suite())
  import AccessControl.tests.testClassSecurityInfo
  suite.addTest(AccessControl.tests.testClassSecurityInfo.test_suite())
  import AccessControl.tests.testImplementation
  suite.addTest(AccessControl.tests.testImplementation.test_suite())
  import AccessControl.tests.testModuleSecurity
  # we allow part of os module, so adjust this test for another not allowed module
  def test_unprotected_module(self):
    self.assertUnauth('subprocess', ())
  AccessControl.tests.testModuleSecurity.ModuleSecurityTests.test_unprotected_module = test_unprotected_module
  suite.addTest(AccessControl.tests.testModuleSecurity.test_suite())
  import AccessControl.tests.testOwned
  suite.addTest(AccessControl.tests.testOwned.test_suite())
  import AccessControl.tests.testPasswordDigest
  suite.addTest(AccessControl.tests.testPasswordDigest.test_suite())
  import AccessControl.tests.testPermissionMapping
  suite.addTest(AccessControl.tests.testPermissionMapping.test_suite())
  import AccessControl.tests.testPermissionRole
  suite.addTest(AccessControl.tests.testPermissionRole.test_suite())
  import AccessControl.tests.testRole
  suite.addTest(AccessControl.tests.testRole.test_suite())
  import AccessControl.tests.testSecurityManager
  suite.addTest(AccessControl.tests.testSecurityManager.test_suite())
  import AccessControl.tests.testZCML
  suite.addTest(AccessControl.tests.testZCML.test_suite())
  import AccessControl.tests.testZopeGuards

  # patch so that AccessControl.tests.testZopeGuards.TestActualPython.testPython
  # also exercise our additions. This test checks that all safe builtins are tested
  TestActualPython_compile = AccessControl.tests.testZopeGuards.TestActualPython._compile
  def _compile(self, fname):
    if fname == 'actual_python.py':
      with open(os.path.join(
          os.path.dirname(AccessControl.tests.testZopeGuards.__file__),
          fname
        )) as infile:
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w') as outfile:
          outfile.write(
              infile.read() + textwrap.dedent(
              '''\
              def erp5_patch():
                  assert next(iter([True, ])) == True
                  assert list(sorted([3,2,1])) == [1, 2, 3]
                  assert list(reversed([3,2,1])) == [1, 2, 3]
              erp5_patch()
                '''
          ))
          outfile.flush()
          return TestActualPython_compile(self, outfile.name)
    return TestActualPython_compile(self, fname)
  AccessControl.tests.testZopeGuards.TestActualPython._compile = _compile
  suite.addTest(AccessControl.tests.testZopeGuards.test_suite())

  import AccessControl.tests.testZopeSecurityPolicy
  suite.addTest(AccessControl.tests.testZopeSecurityPolicy.test_suite())

  return suite