##############################################################################
#
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

import unittest
import zodbpickle
import zodbpickle.fastpickle as pickle
import re
import xml.sax
from io import BytesIO, StringIO

from Products.ERP5Type.XMLExportImport import ppml
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
    return str(ppml.ToXMLUnpickler(f).load())

  def load_from_xml(self, xml_string):
    output = StringIO()
    F=ppml.xmlPickler()
    F.file = output
    F.binary = 1 # XML pickle actually only supports the case of binary = 1

    content_handler = xml.sax.handler.ContentHandler()
    content_handler.startElement = F.unknown_starttag
    content_handler.endElement = F.unknown_endtag
    content_handler.characters = F.handle_data
    xml.sax.parseString(xml_string, content_handler)

    reconstructed_pickled_data = F._stack[0][0]
    return pickle.loads(reconstructed_pickled_data)

  def dump_and_load(self, obj):
    return self.load_from_xml(self.dump_to_xml(obj))


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
    def check_int(v):
      reconstructed = self.dump_and_load(v)
      self.assertEqual(reconstructed, v)
      self.assertIs(type(reconstructed), int)
    check_int(-0)
    check_int(1)
    check_int(-1)
    check_int(0xff)
    check_int(0xff1)
    check_int(0xffff)
    check_int(0xffff1)

  def test_float(self):
    def check_float(v):
      reconstructed = self.dump_and_load(v)
      self.assertEqual(reconstructed, v)
      self.assertIs(type(reconstructed), float)
    check_float(-0.0)
    check_float(1.0)
    check_float(-1.0)
    check_float(.1 + .2)

  def test_None(self):
    self.assertIs(
      self.dump_and_load(None), None)

  def test_bytes(self):
    self.assertEqual(self.dump_and_load(b"bytes"), b"bytes")
    self.assertEqual(self.dump_and_load(b"long bytes" * 100), b"long bytes" * 100)
    self.assertEqual(
      self.dump_and_load(zodbpickle.binary(b"bytes")),
      zodbpickle.binary(b"bytes"))
    self.assertIs(type(self.dump_and_load(zodbpickle.binary(b"bytes"))), zodbpickle.binary)

  def test_unicode(self):
    self.assertIs(type(self.dump_and_load(u"OK")), six.text_type)
    self.assertEqual(self.dump_and_load(u"short"), u"short")
    self.assertEqual(self.dump_and_load(u"unicode 👍"), u"unicode 👍")
    self.assertEqual(self.dump_and_load(u"long" * 100), u"long" * 100)
    self.assertEqual(self.dump_and_load(u"long…" * 100), u"long…" * 100)
    self.assertEqual(self.dump_and_load(u">"), u">")
    self.assertEqual(self.dump_and_load(u"a\nb"), u"a\nb")

  def test_dict(self):
    self.assertEqual(
      self.dump_and_load({'a': 1, 'b': 2}), {'a': 1, 'b': 2})

  def test_tuple(self):
    self.assertEqual(
      self.dump_and_load((1, )), (1, ))
    self.assertEqual(
      self.dump_and_load((1, 'two')), (1, 'two'))
    self.assertEqual(
      self.dump_and_load((1, 'two', 3.0)), (1, 'two', 3.0))
    self.assertEqual(
      self.dump_and_load(tuple([1] * 1000)), tuple([1] * 1000))
    self.assertEqual(
      self.dump_and_load(()), ())

  def test_list(self):
    self.assertEqual(
      self.dump_and_load([1]), [1])
    self.assertEqual(
      self.dump_and_load([]), [])
    self.assertEqual(
      self.dump_and_load([1] * 1000), [1] * 1000)

  def test_set(self):
    self.assertEqual(
      self.dump_and_load(set('abc')), set('abc'))

  def test_reference(self):
    ref = []
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
  def test_oid_base64(self):
    # if it looks like an oid, it's bytes
    self.assertEqual(
      self.load_from_xml("""
        <pickle><string encoding="base64">AAAAAAAAAAE=</string></pickle>
      """),
      b"\x00\x00\x00\x00\x00\x00\x00\x01")

  def test_bytes_base64(self):
    # if it does not decode as utf-8 it's bytes
    self.assertEqual(
      self.load_from_xml("""
        <pickle><string encoding="base64">/wA=</string></pickle>
      """),
      b"\xFF\x00")

