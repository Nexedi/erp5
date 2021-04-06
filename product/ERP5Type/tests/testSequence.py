##############################################################################
#
# Copyright (c) 2021 Nexedi SARL and Contributors. All Rights Reserved.
#                     Nicolas Wavrant <nicolas.wavrant@nexedi.com>
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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList, StoredSequence

class TestStoredSequence(ERP5TypeTestCase):

  def afterSetUp(self):
    self.portal = self.getPortalObject()

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  registerSequenceString = ERP5TypeTestCase.registerSequenceString

  def _getCleanupDict(self):
    return {
      "person_module": list(self.portal.person_module.objectIds()),
    }

  def stepLogin(self, sequence):
    self.login()

  def stepCreatePerson(self, sequence):
    sequence['person'] =  self.portal.person_module.newContent(
        id="person",
        title="Person",
    )

  def stepUpdatePerson1(self, sequence):
    sequence['person'].setTitle(sequence['person'].getTitle() + " 1")

  def stepUpdatePerson2(self, sequence):
    sequence['person'].setTitle(sequence['person'].getTitle() + " 2")

  def stepFillSequenceDict(self, sequence):
    sequence["string"] = "a string"
    sequence["int"] = 10
    sequence["float"] = 3.14
    sequence["erp5_document"] = self.portal.person_module.newContent(
      portal_type="Person",
      id="erp5_document_0",
    )
    sequence["list_of_int"] = [1, 2]
    sequence["list_of_erp5_document"] = [
      self.portal.person_module.newContent(
        portal_type="Person",
        id="erp5_document_%d" % i,
      ) for i in range(1, 3)
    ]

  def test_storedSequenceCanRestoreAState(self):
    sequence_id = "sequence_can_restore"
    self.registerSequenceString(sequence_id, """
      stepCreatePerson
    """)
    sequence = StoredSequence(self, sequence_id)
    sequence.setSequenceString("stepUpdatePerson1")
    sequence_list = SequenceList()
    sequence_list.addSequence(sequence)
    sequence_list.play(self)
    self.assertEqual(self.portal.person_module.person.getTitle(), "Person 1")
    trashbin_value = self.portal.portal_trash[sequence_id]
    self.assertEqual(trashbin_value.person_module.person.getTitle(), "Person")
    self.assertEqual(
      trashbin_value.getProperty("serialised_sequence"),
      ({"key": "person", "type": "erp5_object", "value": "person_module/person"},)
    )
    self.portal.person_module.manage_delObjects(ids=["person"])
    # Run new sequence, with same base sequence.
    # Update the title of the person document in the trashbin to be
    # sure it has been restored from trash and not created
    trashbin_value.person_module.person.setTitle("Trash Person")
    sequence = StoredSequence(self, sequence_id)
    sequence.setSequenceString("stepUpdatePerson2")
    sequence_list = SequenceList()
    sequence_list.addSequence(sequence)
    sequence_list.play(self)
    self.assertEqual(trashbin_value.person_module.person.getTitle(), "Trash Person")
    self.assertEqual(self.portal.person_module.person.getTitle(), "Trash Person 2")

  def test_serialisationOfSequenceDict(self):
    sequence_id = "serialisation"
    self.registerSequenceString(sequence_id, "stepFillSequenceDict")
    sequence = StoredSequence(self, sequence_id)
    sequence.setSequenceString("stepLogin")
    sequence_list = SequenceList()
    sequence_list.addSequence(sequence)
    sequence_list.play(self)
    sequence_dict = sequence._dict
    # sequence._dict will be recalculated
    sequence.deserialiseSequenceDict(self.portal.portal_trash[sequence_id].serialised_sequence)
    self.assertEqual(
      sequence_dict,
      sequence._dict,
    )

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestStoredSequence))
  return suite
