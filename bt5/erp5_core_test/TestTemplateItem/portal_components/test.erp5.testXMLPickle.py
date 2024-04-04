##############################################################################
# coding: utf-8
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    TAHARA Yusei <yusei@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import base64
import unittest
import zodbpickle
import zodbpickle.fastpickle as pickle
import re
from io import BytesIO
from six import StringIO
from Products.ERP5Type.XMLExportImport import importXML, ppml
import six


class DummyClass:
  """
  A dummy data class
  """

  def __init__(self):
    self.data = []


class XMLPickleTestCase(unittest.TestCase):
  _pickle_protocol = 3
  def dump_to_xml(self, obj):
    pickled_string = pickle.dumps(obj, protocol=self._pickle_protocol)
    f = BytesIO(pickled_string)
    xml = ppml.ToXMLUnpickler(f).load().__str__()
    self.assertIsInstance(xml, str)
    return xml

  def load_from_xml(self, xml_string, persistent_load=None):
    assertEqual = self.assertEqual
    class DummyJar:
      loaded = None
      """follow interface expected by importXML"""
      def importFile(self, file, clue):
        assertEqual(clue, 'ignored')
        assertEqual(file.read(4), b'ZEXP')
        unpickler = pickle.Unpickler(file)
        if persistent_load:
          unpickler.persistent_load = persistent_load
        self.loaded = unpickler.load()

    jar = DummyJar()
    xml_string = '<?xml version="1.0"?>\n<ZopeData>%s</ZopeData>' % xml_string
    importXML(jar, StringIO(xml_string), clue='ignored')
    return jar.loaded

  def dump_and_load(self, obj):
    return self.load_from_xml(self.dump_to_xml(obj))

  def check_and_load(self, v):
    reconstructed = self.dump_and_load(v)
    self.assertEqual(reconstructed, v)
    self.assertIs(type(reconstructed), type(v))


class TestXMLPickle(XMLPickleTestCase):

  def test_reduce(self):
    """
    Make sure that a object which uses reduce for pickling can be pickled by xml pickler.
    This also covers the case of instances
    """
    obj = DummyClass()
    obj.data.append(1)
    obj.data.append(obj)
    obj.data.append(obj.data)

    pattern = re.compile('WAA') # regex pattern object uses reduce.(See sre.py)
    obj.data.append(pattern)

    reconstructed_obj = self.dump_and_load(obj)

    self.assertTrue(reconstructed_obj.__class__ is DummyClass)
    self.assertIs(type(getattr(reconstructed_obj, 'data', None)), list)
    self.assertEqual(reconstructed_obj.data[0], 1)
    self.assertTrue(reconstructed_obj.data[1] is reconstructed_obj)
    self.assertTrue(reconstructed_obj.data[2] is reconstructed_obj.data)
    self.assertTrue(type(reconstructed_obj.data[3]) is type(pattern))
    self.assertEqual(reconstructed_obj.data[3].pattern, 'WAA')

  def test_bool(self):
    self.assertIs(self.dump_and_load(True), True)
    self.assertIs(self.dump_and_load(False), False)

  def test_int(self):
    self.check_and_load(-0)
    self.check_and_load(1)
    self.check_and_load(-1)
    self.check_and_load(0xff)
    self.check_and_load(0xff1)
    self.check_and_load(0xffff)
    self.check_and_load(2**128)
    # long4
    # https://github.com/python/cpython/blob/4d4a6f1b/Lib/test/pickletester.py#L2049-L2050
    self.check_and_load(12345678910111213141516178920 << (256*8))


  if six.PY2:
    def test_long(self):
      self.check_and_load(long(-0))
      self.check_and_load(long(1))
      self.check_and_load(long(-1))
      self.check_and_load(long(0xff))
      self.check_and_load(long(0xff1))
      self.check_and_load(long(0xffff))
      self.check_and_load(long(2**128))
      self.check_and_load(12345678910111213141516178920 << (256*8))

  def test_float(self):
    self.check_and_load(-0.0)
    self.check_and_load(1.0)
    self.check_and_load(-1.0)
    self.check_and_load(.33)

  def test_None(self):
    self.assertIs(
      self.dump_and_load(None), None)

  def test_bytes(self):
    self.check_and_load(b"bytes")
    self.check_and_load(b"long bytes" * 100)
    self.check_and_load(zodbpickle.binary(b"bytes"))
    self.check_and_load(zodbpickle.binary(b""))

  def test_unicode(self):  # BBB PY2
    self.assertIs(type(self.dump_and_load(u"OK")), six.text_type)
    self.check_and_load(u"short")
    self.check_and_load(u"unicode 👍")
    self.check_and_load(u"long" * 100)
    self.check_and_load(u"long…" * 100)
    self.check_and_load(u">")
    self.check_and_load(u"a\nb")
    self.check_and_load(u" with spaces ")
    self.check_and_load(u"\twith\ttabs\t")
    self.check_and_load(u"")

  def test_str(self):
    self.assertIs(type(self.dump_and_load("OK")), str)
    self.check_and_load("short")
    self.check_and_load("unicode 👍")
    self.check_and_load("long" * 100)
    self.check_and_load("long…" * 100)
    self.check_and_load(">")
    self.check_and_load("a\nb")
    self.check_and_load(" with spaces ")
    self.check_and_load("\twith\ttabs\t")
    self.check_and_load("")

  def test_dict(self):
    self.check_and_load({'a': 1, 'b': 2})
    self.check_and_load({'hé': 'ho'})
    self.check_and_load(dict.fromkeys(range(3000)))

  def test_tuple(self):
    self.check_and_load((1, ))
    self.check_and_load((1, 'two'))
    self.check_and_load((1, 'two', 3.0))
    self.check_and_load(tuple([1] * 1000))
    self.check_and_load(())
    self.check_and_load(('hé',))
    self.check_and_load(('hé', 'hé'))
    self.check_and_load(('hé', 'hé', 'hé'))
    self.check_and_load(('hé', 'hé', 'hé', 'hé'))

  def test_list(self):
    self.check_and_load([1])
    self.check_and_load([])
    self.check_and_load([1] * 1000)
    self.check_and_load(['hé'])

  def test_set(self):
    self.check_and_load(set('abc'))
    self.check_and_load(set('hé'))
    self.check_and_load(set([]))

  def test_reference(self):
    ref = []
    reconstructed = self.dump_and_load([ref, ref, ref])
    self.assertEqual(reconstructed, [ref, ref, ref])
    self.assertIs(reconstructed[0], reconstructed[1])

  def test_reference_long(self):
    # same as reference (which is using BINPUT/BINGET but with large data
    # to use LONG_BINPUT/LONG_BINGET)
    ref = [list() for _ in range(256)]
    reconstructed = self.dump_and_load([ref, ref, ref])
    self.assertEqual(reconstructed, [ref, ref, ref])
    self.assertIs(reconstructed[0], reconstructed[1])


class TestXMLPickleStringEncoding(XMLPickleTestCase):
  def test_string_base64(self):
    self.assertEqual(
      self.load_from_xml("""
        <pickle><string encoding="base64">d2l0aApuZXdsaW5l</string></pickle>
      """),
      "with\nnewline")

  def test_string_repr(self):
    self.assertEqual(
      self.load_from_xml("""
        <pickle><string encoding="repr">a\\'1</string></pickle>
      """),
      "a'1")
    # repr is default encoding
    self.assertEqual(
      self.load_from_xml("""
        <pickle><string>a\\'1</string></pickle>
      """),
      "a'1")

  def test_string_cdata(self):
    self.assertEqual(
      self.load_from_xml("""
<pickle><string encoding="cdata"><![CDATA[

<p></p>

]]></string></pickle>"""),
"<p></p>")


class TestXMLPickleStringHeuristics(XMLPickleTestCase):
  """Heuristics to map python2 str to unicode or bytes in business templates.
  """

  def test_bytes_base64(self):
    # if it does not decode as utf-8, it's bytes
    self.assertEqual(
      self.load_from_xml("""
        <pickle><string encoding="base64">/wA=</string></pickle>
      """),
      b"\xFF\x00")

  def test_long_bytes_base64(self):
    # if it does not decode as utf-8, it's bytes
    long_bytes = b"\xFF\x00" * 256
    self.assertEqual(
      self.load_from_xml("""
        <pickle><string encoding="base64">%s</string></pickle>
      """ % base64.b64encode(long_bytes).decode()),
      long_bytes)

  def test_string_persistent_id_base64(self):
    # persistent ids are loaded as bytes
    persistent_ids = []
    def persistent_load(oid):
      persistent_ids.append(oid)
    self.assertEqual(
      self.load_from_xml("""
      <pickle>
        <persistent>
          <string encoding="base64">AAAAAAAAAAE=</string>
        </persistent>
      </pickle>
      """,
      persistent_load=persistent_load),
      None)
    self.assertEqual(
      persistent_ids,
      [b'\x00\x00\x00\x00\x00\x00\x00\x01'])
