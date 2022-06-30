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

import json
import os.path
import tempfile
import textwrap
import unittest
import uuid

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Type.tests.utils import removeZODBPythonScript
from Products.ERP5Type.patches.Restricted import allow_class_attribute
from Products.ERP5Type.patches.Restricted import (pandas_black_list, dataframe_black_list, series_black_list)
from AccessControl import Unauthorized
from AccessControl.ZopeGuards import Unauthorized as ZopeGuardsUnauthorized

class TestRestrictedPythonSecurity(ERP5TypeTestCase):
  """
    Test Restricted Python Security that is monkey patched by ERP5.
  """

  def getTitle(self):
    return "Restricted Python Security Test"

  def runScript(self, container, name, kwargs):
    func = getattr(self.portal, name)
    return func(**kwargs)

  def createAndRunScript(self, code, **kwargs):
    # we do not care the script name for security test thus use uuid1
    name = str(uuid.uuid1())
    expected = kwargs.get('expected', None)
    script_container = self.portal.portal_skins.custom
    try:
      createZODBPythonScript(script_container, name, '**kw', textwrap.dedent(code))
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
    self.createAndRunScript('''
        import datetime
        return datetime.datetime.now()
        ''')
    self.createAndRunScript('''
        import datetime
        return datetime.time.max
        ''')
    self.createAndRunScript('''
        import datetime
        return datetime.date.today()
        ''')
    self.createAndRunScript('''
        import datetime
        return datetime.timedelta.min
        ''')
    self.createAndRunScript('''
        import datetime
        return datetime.tzinfo
        ''')
    self.createAndRunScript('''
        import datetime
        return datetime.datetime.strptime('', '')
        ''')

  def testDictClassMethod(self):
    # This is intended to be allowed from the beggining
    self.createAndRunScript("return dict.fromkeys(['a', 'b', 'c'])")

  def testDecimalClassMethod(self):
    # Now it is not allowed
    self.assertRaises(
        Unauthorized,
        self.createAndRunScript,
        '''
        import decimal
        return decimal.Decimal.from_float(3.3)
        ''')

    # allow it only in this test class to check
    import decimal
    allow_class_attribute(decimal.Decimal, {"from_float":1})
    # make sure now we can run without raising Unauthorized
    self.createAndRunScript('''
        import decimal
        return decimal.Decimal.from_float(3.3)
        ''')

  def test_urlparse(self):
    self.createAndRunScript('''
        import urlparse
        return urlparse.urlparse("http://example.com/pa/th/?q=s").path
        ''',
        expected='/pa/th/'
    )
    # access computed attributes (property) is also OK
    self.createAndRunScript('''
        import urlparse
        return urlparse.urlparse("http://example.com/pa/th/?q=s").hostname
        ''',
        expected='example.com'
    )
    self.createAndRunScript('''
        import urlparse
        return urlparse.urlsplit("http://example.com/pa/th/?q=s").path
        ''',
        expected='/pa/th/'
    )
    self.createAndRunScript('''
        import urlparse
        return urlparse.urldefrag("http://example.com/#frag")[1]
        ''',
        expected='frag'
    )
    self.createAndRunScript('''
        import urlparse
        return urlparse.parse_qs("q=s")
        ''',
        expected={'q': ['s']}
    )
    self.createAndRunScript('''
        import urlparse
        return urlparse.parse_qsl("q=s")
        ''',
        expected=[('q', 's')]
    )

  def testRandom(self):
    self.createAndRunScript('''
        import random
        return random.Random().getrandbits(10)
        ''')

  def testSystemRandom(self):
    self.createAndRunScript('''
        import random
        return random.SystemRandom().getrandbits(10)
        ''')

  def test_os_urandom(self):
    self.createAndRunScript('''
        import os
        return os.urandom(10)
        ''')
    # other "unsafe" os members are not exposed
    self.assertRaises(
        Unauthorized,
        self.createAndRunScript,
        '''
        import os
        return os.path.exists("/")
        ''')
    self.assertRaises(
        Unauthorized,
        self.createAndRunScript,
        '''
        import os
        return os.system
        ''')
    self.assertRaises(Unauthorized,
      self.createAndRunScript, 'from os import system')

  def test_set(self):
    self.createAndRunScript('''
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
        ''')

  def test_frozenset(self):
    self.createAndRunScript('''
        s = frozenset([1, 2])
        s.copy()
        s.difference([1])
        s.intersection([1])
        s.isdisjoint([1])
        s.issubset([1])
        s.issuperset([1])
        s.symmetric_difference([1])
        s.union([1])
        ''')

  def test_sorted(self):
    self.createAndRunScript('''
        returned = []
        for i in sorted([2, 3, 1]):
          returned.append(i)
        return returned
        ''',
        expected=[1, 2, 3],
    )

  def test_reversed(self):
    self.createAndRunScript('''
        returned = []
        for i in reversed(('3', '2', '1')):
          returned.append(i)
        return returned
        ''',
        expected=['1', '2', '3'],
    )
    self.createAndRunScript('''
        returned = []
        for i in reversed([3, 2, 1]):
          returned.append(i)
        return returned
        ''',
        expected=[1, 2, 3],
    )
    self.createAndRunScript('''
        returned = []
        for i in reversed('321'):
          returned.append(i)
        return returned
        ''',
        expected=['1', '2', '3'],
    )

  def test_enumerate(self):
    self.createAndRunScript('''
        returned = []
        for i in enumerate(["zero", "one", "two",]):
          returned.append(i)
        return returned
        ''',
        expected=[(0, "zero"), (1, "one"), (2, "two"), ],
    )
    # with start= argument
    self.createAndRunScript('''
        returned = []
        for i in enumerate(["one", "two", "three"], start=1):
          returned.append(i)
        return returned
        ''',
        expected=[(1, "one"), (2, "two"), (3, "three")],
    )

  def test_generator_iteration(self):
    generator_iteration_script = textwrap.dedent(
        '''
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

    self.createAndRunScript('''
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
        ''',
        kwargs={'generator': generator_with_not_allowed_objects()},
        expected=["one", "Unauthorized()", 2],
    )

  def test_json(self):
    self.createAndRunScript('''
        import json
        return json.loads(json.dumps({"ok": [True]}))
        ''',
        expected={"ok": [True]}
    )

  def test_calendar(self):
    self.createAndRunScript('''
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
        ''')

  def test_collections_Counter(self):
    self.createAndRunScript('''
        from collections import Counter
        c = Counter(["a", "b"])
        c["a"] = c["a"] + 1
        del c["b"]
        c.update({"a": 1})
        return c.most_common(1)
        ''',
        expected=[('a', 3)]
    )

  def test_collections_defaultdict(self):
    self.createAndRunScript('''
        from collections import defaultdict
        d = defaultdict(list)
        d["x"].append(1)
        d["y"] = 2
        del d["y"]
        return d
        ''',
        expected={"x": [1]}
    )

  def test_collections_namedtuple(self):
    self.createAndRunScript('''
        from collections import namedtuple
        Object = namedtuple("Object", ["a", "b", "c"])
        return Object(a=1, b=2, c=3).a
        ''',
        expected=1
    )
    # also make sure we can iterate on nametuples
    self.createAndRunScript('''
        from collections import namedtuple
        Object = namedtuple("Object", ["a", "b", "c"])
        returned = []
        for x in Object(a=1, b=2, c=3):
          returned.append(x)
        return returned
        ''',
        expected=[1, 2, 3]
    )

  def test_collections_OrderedDict(self):
    self.createAndRunScript('''
        from collections import OrderedDict
        d = OrderedDict()
        d["a"] = 1
        d["b"] = 2
        d["c"] = 3
        del d["c"]
        return list(d.items())
        ''',
        expected=[("a", 1), ("b", 2)]
    )

  def test_lax_name(self):
    self.createAndRunScript('''
        def _function():
          pass
        class SimpleObject:
          def __init__(self):
            self.attribute = 1
          def _method(self):
            _variable = 1
        return SimpleObject().attribute
        ''',
        expected=1
    )

  def test_StringIO(self):
    self.createAndRunScript('''
        import StringIO
        s = StringIO.StringIO()
        s.write("ok")
        return s.getvalue()
        ''',
        expected="ok"
    )
    self.createAndRunScript('''
        import StringIO
        return StringIO.StringIO("ok").getvalue()
        ''',
        expected="ok"
    )

  def test_cStringIO(self):
    self.createAndRunScript('''
        import cStringIO
        s = cStringIO.StringIO()
        s.write("ok")
        return s.getvalue()
        ''',
        expected="ok"
    )
    self.createAndRunScript('''
        import cStringIO
        return cStringIO.StringIO("ok").getvalue()
        ''',
        expected="ok"
    )

  def testNumpy(self):
    self.createAndRunScript('''
        import numpy as np
        return [x for x in (np.dtype('int32').name, np.timedelta64(1, 'D').nbytes)]
        ''',
        expected=["int32", 8]
    )

  def testNdarrayWrite(self):
    self.createAndRunScript('''
        import numpy as np
        z = np.array([[1,2],[3,4]])
        z[0][0] = 99
        return z[0][0]
        ''',
        expected=99
    )

  def testPandasSeries(self):
    self.createAndRunScript('''
        import pandas as pd
        return pd.Series([1,2,3]).tolist()
        ''',
        expected=[1,2,3]
    )

  def testPandasTimestamp(self):
    self.createAndRunScript('''
        import pandas as pd
        return pd.Timestamp('2020-01').year
        ''',
        expected=2020
    )

  def testPandasDatetimeIndex(self):
    self.createAndRunScript('''
        import pandas as pd
        df = pd.DataFrame({'date':['2020-01-01','2020-03-01']})
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return str(df.index.name)
        ''',
        expected='date'
    )

  def testPandasMultiIndex(self):
    self.createAndRunScript('''
        import pandas as pd
        df = pd.DataFrame({'a':[1,2],'b':[3,4],'c':[5,6]})
        df2 = df.set_index(['a','b'],drop=True)
        return list(df2.index.names)
        ''',
        expected=['a','b']
    )

  def testPandasIndex(self):
    self.createAndRunScript('''
        import pandas as pd
        df = pd.DataFrame({'a':[1,2],'b':[3,4]})
        df2 = df.set_index(['a'],drop=True)
        return list(df2.index.names)
        ''',
        expected=['a']
    )

  def testPandasGroupBy(self):
    # test pandas.core.groupby.DataFrameGroupBy,SeriesGroupBy
    self.createAndRunScript('''
        import pandas as pd
        df2 = pd.DataFrame({'id':[1,1,2],'quantity':[3,4,5],'price':[6,7,8]})
        return list(df2.groupby(['id'])['quantity'].agg('sum'))
        ''',
        expected=[7,5]
    )

  def testPandasLocIndexer(self):
    self.createAndRunScript('''
        import pandas as pd
        df = pd.DataFrame({'a':[1,2],'b':[3,4]})
        return df.loc[df['a'] == 1]['b'][0]
        ''',
        expected=3
    )

  def testPandasDataFrameWrite(self):
    self.createAndRunScript('''
        import pandas as pd
        df = pd.DataFrame({'a':[1,2], 'b':[3,4]})
        df.iloc[0, 0] = 999
        return df['a'][0]
        ''',
        expected=999
    )

  def testPandasIORead(self):
    # Test the black_list configuration validity
    for read_method in pandas_black_list:
      self.assertRaises(
          Unauthorized,
          self.createAndRunScript,
          '''
          import pandas as pd
          read_method = pd.{read_method}
          read_method('testPandasIORead.data')
          '''.format(read_method=read_method))

  def testPandasDataFrameIOWrite(self):
    self.assertRaises(
        ZopeGuardsUnauthorized,
        self.createAndRunScript,
        '''
        import pandas as pd
        df = pd.DataFrame({'a':[1,2,3]})
        df.to_csv('testPandasDataFrameIOWrite.csv')
        ''')

    # Test the black_list configuration validity
    for write_method in dataframe_black_list:
      self.assertRaises(
          ZopeGuardsUnauthorized,
          self.createAndRunScript,
          '''
          import pandas as pd
          df = pd.DataFrame(columns=['a','b'],data=[[1,2]])
          write_method = df.{write_method}
          write_method('testPandasDataFrameIOWrite.data')
          '''.format(write_method=write_method))

  def testPandasSeriesIOWrite(self):
    self.assertRaises(
        ZopeGuardsUnauthorized,
        self.createAndRunScript,
        '''
        import pandas as pd
        df = pd.Series([4,5,6])
        df.to_csv('testPandasSeriesIOWrite.csv')
        ''')

    # Test the black_list configuration validity
    for write_method in series_black_list:
      self.assertRaises(
          ZopeGuardsUnauthorized,
          self.createAndRunScript,
          '''
          import pandas as pd
          df = pd.Series([4,5,6])
          write_method = df.{write_method}
          write_method('testPandasSeriesIOWrite.data')
          '''.format(write_method=write_method))

  def _assertPandasRestrictedReadFunctionIsEqualTo(
    self, read_function, read_argument, expected_data_frame_init
  ):
    self.createAndRunScript(
      '''
      import pandas as pd
      expected_data_frame = pd.DataFrame({expected_data_frame_init})
      return pd.{read_function}({read_argument}).equals(expected_data_frame)
      '''.format(
        expected_data_frame_init=expected_data_frame_init,
        read_function=read_function,
        read_argument=read_argument,
      ),
      expected=True
    )

  def testPandasRestrictedReadFunctionProhibitedInput(self):
    """
      Test if patched pandas read_* functions raise with any input which isn't a string.
    """
    for pandas_read_function in ("read_json", "read_csv", "read_fwf"):
      for preparation, prohibited_input in (
        ('', 100),
        ('from StringIO import StringIO', 'StringIO("[1, 2, 3]")'),
      ):
        self.assertRaises(
          ZopeGuardsUnauthorized,
          self.createAndRunScript,
          '''
          import pandas as pd
          {preparation}
          pd.{pandas_read_function}({prohibited_input})
          '''.format(
            preparation=preparation,
            pandas_read_function=pandas_read_function,
            prohibited_input=prohibited_input,
          )
        )
  def testPandasReadFwf(self):
    read_function = "read_fwf"
    # Normal input should be correctly handled
    self._assertPandasRestrictedReadFunctionIsEqualTo(
      read_function, r'"100\n200"', r"[[200]], columns=['100']",
    )
    # Ensure monkey patch parses keyword arguments to patched function
    self._assertPandasRestrictedReadFunctionIsEqualTo(
      read_function, r'"1020\n3040", widths=[2, 2]', r"[[30, 40]], columns=['10', '20']",
    )
    # A string containing an url or file path should be handled as if
    # it would be a normal csv string entry
    self._assertPandasRestrictedReadFunctionIsEqualTo(
      read_function,
       r'"file://path/to/fwf/file.fwf"',
       r"[], columns=['file://path/to/fwf/file.fwf']",
    )

  def testPandasReadCSV(self):
    read_function = "read_csv"
    # Normal input should be correctly handled
    self._assertPandasRestrictedReadFunctionIsEqualTo(
      read_function,
       r'"11,2,300\n50.5,99,hello"',
       r"[[50.5, 99, 'hello']], columns='11 2 300'.split(' ')",
    )
    # Ensure monkey patch parses keyword arguments to patched function
    self._assertPandasRestrictedReadFunctionIsEqualTo(
      read_function, r'"a;b", sep=";"', r"[], columns=['a', 'b']",
    )
    # A string containing an url or file path should be handled as if
    # it would be a normal csv string entry
    self._assertPandasRestrictedReadFunctionIsEqualTo(
      read_function,
      r'"https://people.sc.fsu.edu/~jburkardt/data/csv/addresses.csv"',
      r"[], columns=['https://people.sc.fsu.edu/~jburkardt/data/csv/addresses.csv']",
    )
    self._assertPandasRestrictedReadFunctionIsEqualTo(
      read_function,
      r'"file://path/to/csv/file.csv"',
      r"[], columns=['file://path/to/csv/file.csv']",
    )

  def testPandasReadJsonParsesInput(self):
    read_function = "read_json"
    # Normal input should be correctly handled
    self._assertPandasRestrictedReadFunctionIsEqualTo(
      read_function, '"[1, 2, 3]"', "[1, 2, 3]"
    )
    self._assertPandasRestrictedReadFunctionIsEqualTo(
      read_function,
      '\'{"column_name": [1, 2, 3], "another_column": [3, 9.2, 100]}\'',
      '{"column_name": [1, 2, 3], "another_column": [3, 9.2, 100]}',
    )
    # Ensure monkey patch parses keyword arguments to patched function
    self._assertPandasRestrictedReadFunctionIsEqualTo(
      read_function,
      r'"[1, 2, 3]\n[4, 5, 6]", lines=True',
      "[[1, 2, 3], [4, 5, 6]]",
    )
    # URLs, etc. should raise a ValueError
    # (see testPandasReadJsonProhibitsMalicousString)

  def testPandasReadJsonProhibitsMalicousString(self):
    """
      Test if file path, urls and other bad strings
      raise value errors
    """

    # Create valid json file which could be read
    # by a non-patched read_json function.
    test_file_path = ".testPandasReadJson.json"
    json_test_data = [1, 2, 3]
    with open(test_file_path, 'w') as json_file:
      json.dump(json_test_data, json_file)
    self.addCleanup(os.remove, test_file_path)

    # Ensure json creation was successful
    self.assertTrue(os.path.isfile(test_file_path))
    with open(test_file_path, "r") as json_file:
      self.assertEqual(json_test_data, json.loads(json_file.read()))

    for malicous_input in (
      # If pandas would read this as an URL it should
      # raise an URLError. But because it will try
      # to read it as a json string, it will raise
      # a ValueError.
      "https://test-url.com/test-name.json",
      "file://path/to/json/file.json",
      # This shouldn't raise any error in case
      # pandas read function wouldn't be patched.
      test_file_path,
      # Gibberish should also raise a ValueError
      "Invalid-string"
    ):
      self.assertRaises(
        ValueError,
        self.createAndRunScript,
        '''
        import pandas as pd
        pd.read_json("{}")
        '''.format(malicous_input)
      )

  def testIpAddressModuleAllowance(self):
    # Test ipaddress usability
    self.createAndRunScript('import ipaddress')
    self.createAndRunScript('''
        from ipaddress import ip_address
        return ip_address('90.4.85.17').is_global
        ''')
    self.createAndRunScript('''
        from ipaddress import ip_network
        return ip_network('90.4.0.0/16').is_private
        ''')
    self.createAndRunScript('''
        from ipaddress import ip_address, ip_network
        return ip_address('90.4.85.17') in ip_network('90.4.0.0/16')
        ''')
    self.createAndRunScript('''
        from ipaddress import ip_interface
        return ip_interface('90.4.85.17').with_prefixlen
        ''')

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
  # Disable crypt scheme, we don't want to use CRYPT and it fails on debian 11.
  # This is also disabled in github.com/zopefoundation/AuthEncoding commit
  # fbbdcf3 (Allow the CRYPT test to fail as it is the case on GHA., 2021-04-08)
  import AccessControl.AuthEncoding
  def setUp(self):
    self._original_AuthEncoding_schemes = AccessControl.AuthEncoding._schemes[::]
    AccessControl.AuthEncoding._schemes = [s for s in AccessControl.AuthEncoding._schemes if s[0] != 'CRYPT']
  AccessControl.tests.testPasswordDigest.PasswordDigestTests.setUp = setUp
  def tearDown(self):
    AccessControl.AuthEncoding._schemes = self._original_AuthEncoding_schemes
  AccessControl.tests.testPasswordDigest.PasswordDigestTests.tearDown = tearDown
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