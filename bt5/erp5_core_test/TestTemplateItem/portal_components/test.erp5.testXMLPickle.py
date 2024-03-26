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
import pickle
import re
import xml.sax
from six.moves import cStringIO as StringIO
from io import BytesIO

from Products.ERP5Type.XMLExportImport import ppml


class DummyClass:
  """
  A dummy data class
  """

  def __init__(self):
    self.data = []


class TestXMLPickle(unittest.TestCase):

  def test_reduce(self):
    """
    Make sure that a object which uses reduce for pickling can be pickled by xml pickler.
    """
    obj = DummyClass()
    obj.data.append(1)
    obj.data.append(obj)
    obj.data.append(obj.data)

    pattern = re.compile('WAA') # regex pattern object uses reduce.(See sre.py)
    obj.data.append(pattern)

    pickled_string = pickle.dumps(obj, protocol=2)
    f = BytesIO(pickled_string)
    xmldata = str(ppml.ToXMLUnpickler(f).load())

    output = StringIO()

    F=ppml.xmlPickler()
    F.file = output
    F.binary = 1

    content_handler = xml.sax.handler.ContentHandler()
    content_handler.startElement = F.unknown_starttag
    content_handler.endElement = F.unknown_endtag
    content_handler.characters = F.handle_data
    xml.sax.parseString(xmldata, content_handler)

    reconstructed_pickled_data = F._stack[0][0]
    reconstructed_obj = pickle.loads(reconstructed_pickled_data)

    self.assertTrue(reconstructed_obj.__class__ is DummyClass)
    self.assertTrue(type(getattr(reconstructed_obj, 'data', None)) is list)  # pylint:disable=unidiomatic-typecheck
    self.assertEqual(reconstructed_obj.data[0], 1)
    self.assertTrue(reconstructed_obj.data[1] is reconstructed_obj)
    self.assertTrue(reconstructed_obj.data[2] is reconstructed_obj.data)
    self.assertTrue(type(reconstructed_obj.data[3]) is type(pattern))
    self.assertEqual(reconstructed_obj.data[3].pattern, 'WAA')
