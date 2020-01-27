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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Type.tests.utils import removeZODBPythonScript
from Products.ERP5Type.patches.Restricted import allow_class_attribute
from AccessControl import Unauthorized
import uuid

class TestRestrictedPythonSecurity(ERP5TypeTestCase):
  """
    Test Restricted Python Security that is monkey patched by ERP5.
  """

  def getTitle(self):
    return "Restricted Python Security Test"

  def runScript(self, container, name):
    func = getattr(self.portal, name)
    return func()

  def createAndRunScript(self, *args, **kwargs):
    # we do not care the script name for security test thus use uuid1
    name = str(uuid.uuid1())
    code = '\n'.join(args)
    expected = kwargs.get('expected', None)
    script_container = self.portal.portal_skins.custom
    try:
      createZODBPythonScript(script_container, name, '**kw', code)
      if expected:
        self.assertEqual(self.runScript(script_container, name), expected)
      else:
        self.runScript(script_container, name)
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
  def test_collections_Counter(self):
    self.createAndRunScript(
        'from collections import Counter',
        'c = Counter(["a", "b"])',
        'c["a"] = c["a"] + 1',
        'c.update({"a": 1})',
        'return c.most_common(1)',
        expected=[('a', 3)]
    )

  def test_collections_namedtuple(self):
    self.createAndRunScript(
        'from collections import namedtuple',
        'Object = namedtuple("Object", ["a", "b", "c"])',
        'return Object(a=1, b=2, c=3).a',
        expected=1
    )
