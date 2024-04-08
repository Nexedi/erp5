##############################################################################
#
# Copyright (c) 2002-2012 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################


from erp5.component.module.testERP5SyncMLMixin import TestERP5SyncMLMixin
from six.moves import range


class testSyncMLAsynchronousEngine(TestERP5SyncMLMixin):
  """
  Test SyncML in Asynchronous mode
  """

  def getTitle(self):
    return "Test SyncML with asynchronous engine"

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.sync_tool = self.portal.portal_synchronizations
    self.portal.z_drop_syncml()
    self.portal.z_create_syncml()
    # here, you can create the categories and objects your test will depend on

  def _initSyncModule(self):
    """
    Init and clear modules used in sync test
    """
    self.client_module = self.portal.get('syncml_test_person_client_module', None)
    self.server_module = self.portal.get('syncml_test_person_server_module', None)
    self.assertNotEqual(self.client_module, None)
    self.assertNotEqual(self.server_module, None)
    self.client_module.manage_delObjects(ids=list(self.client_module.objectIds()))
    self.server_module.manage_delObjects(ids=list(self.server_module.objectIds()))
    self.assertEqual(len(self.client_module), 0)
    self.assertEqual(len(self.server_module), 0)

  def _initSynchronization(self):
    """ Init pubs & subs """
    self.pub = self.sync_tool.get("test_person_pub")
    self.sub = self.sync_tool.get("test_person_sub")
    self.assertNotEqual(self.pub, None)
    self.assertNotEqual(self.sub, None)
    if not self.pub.getValidationState() == "validated":
      self.pub.validate()
    if not self.sub.getValidationState() == "validated":
      self.sub.validate()
    # Reset from previous sync
    self.sub.SyncMLSubscription_resetSubscription()
    self.pub.SyncMLPublication_resetPublication()
    # Make sure of initial state of sub
    if self.sub.getSynchronizationState() not in ("finished",
                                             "not_running"):
      self.sub.finish()
    # Use url of the current site
    self.updateSynchronizationURL(
      url=self.portal.absolute_url().replace('//', '//syncml:syncml@'),
      object_list = [self.pub, self.sub])
    # Update authentication
    user = password = "syncml"
    self.addSynchronizationUser(user, password)
    self.updateAuthenticationCredentials(user, password, [self.sub,])

  def _updateSyncMLPreference(self, activity_count=100, doc_count=30,
                              sync_count=0):
    pref = self.portal.portal_preferences.getActiveSystemPreference()
    if not pref:
      pref = self.portal.portal_preferences.newContent(
        portal_type="System Preference")
    pref.edit(preferred_document_retrieved_per_activity_count=doc_count,
              preferred_retrieval_activity_count=activity_count,
              preferred_sync_action_per_activity_count=sync_count)
    if not pref.getPreferenceState() != "enabled":
      pref.enable()

  def _fillModule(self, module, nb_objects):
    self.title_list = []
    append = self.title_list.append
    for x in range(nb_objects):
      module.newContent(title=str(x))
      append(str(x))

  def _setSyncMode(self, mode):
    self.sub.edit(syncml_alert_mode=mode)

  def test_01(self, *args, **kw):
    """
    test the synchronization without splitting of sync action in activities
    We generate 3 activity of 5 documents and synchronizing 50 documents
    so that getAndActivate will be call many times
    """
    self._initSynchronization()
    self._initSyncModule()
    self.tic()
    # Init the sync
    self._updateSyncMLPreference(activity_count=3, doc_count=5)  # Process 15 docs
    nb_document=50
    self._fillModule(module=self.client_module, nb_objects=nb_document)
    self._setSyncMode("refresh_from_client_only")
    self.tic()
    # Initial check
    self.assertEqual(len(self.client_module), nb_document)
    self.assertEqual(len(self.server_module), 0)
    # Do the sync
    self.sync_tool.processClientSynchronization(self.sub.getRelativeUrl())
    self.tic()
    # Check result
    self.assertEqual(self.sub.getSynchronizationState(), "finished")
    self.assertEqual(len(self.client_module), nb_document)
    self.assertEqual(len(self.server_module), nb_document)
    self.assertEqual(len(self.title_list), 50)
    for person in self.server_module.objectValues():
      self.title_list.remove(person.getTitle())
    self.assertEqual(len(self.title_list), 0)

  def test_02_noSyncCommandSplitting(self, *args, **kw):
    """
    test the synchronization without splitting of sync action in activities
    We generate 35activity of 5 documents and synchronizing 50 documents
    so that getAndActivate will be call two times only, and the last row
    of document will have the length of the limit defined (25)
    """
    self._initSynchronization()
    self._initSyncModule()
    self.tic()
    # Init the sync
    self._updateSyncMLPreference(activity_count=5, doc_count=5)  # Process 25 docs
    nb_document=50
    self._fillModule(module=self.client_module, nb_objects=nb_document)
    self._setSyncMode("refresh_from_client_only")
    self.tic()
    # Initial check
    self.assertEqual(len(self.client_module), nb_document)
    self.assertEqual(len(self.server_module), 0)
    # Do the sync
    self.sync_tool.processClientSynchronization(self.sub.getRelativeUrl())
    self.tic()
    # Check result
    self.assertEqual(self.sub.getSynchronizationState(), "finished")
    self.assertEqual(len(self.client_module), nb_document)
    self.assertEqual(len(self.server_module), nb_document)
    self.assertEqual(len(self.title_list), 50)
    for person in self.server_module.objectValues():
      self.title_list.remove(person.getTitle())
    self.assertEqual(len(self.title_list), 0)


  def test_03(self, *args, **kw):
    """
    test the synchronization without splitting of sync action in activities
    We generate 3 activity of 5 documents and synchronizing 12 documents
    so that getAndActivate will be call one time and final activity must on 2
    documents
    Note that this test pass even if final activity contains more documents as
    we are processing activity on one node only and so the same document creation
    process can't be done in parralell and result in the same document created twice
    This is has to be unit tested at the Subscription level with mock objects
    """
    self._initSynchronization()
    self._initSyncModule()
    self.tic()
    # Init the sync
    self._updateSyncMLPreference(activity_count=3, doc_count=5)  # Process 15 docs
    nb_document=12
    self._fillModule(module=self.client_module, nb_objects=nb_document)
    self._setSyncMode("refresh_from_client_only")
    self.tic()
    # Initial check
    self.assertEqual(len(self.client_module), nb_document)
    self.assertEqual(len(self.server_module), 0)
    # Do the sync
    self.sync_tool.processClientSynchronization(self.sub.getRelativeUrl())
    self.tic()
    # Check result
    self.assertEqual(self.sub.getSynchronizationState(), "finished")
    self.assertEqual(len(self.client_module), nb_document)
    self.assertEqual(len(self.server_module), nb_document)
    self.assertEqual(len(self.title_list), nb_document)
    for person in self.server_module.objectValues():
      self.title_list.remove(person.getTitle())
    self.assertEqual(len(self.title_list), 0)


  def test_05_SyncMLSubscription(self):
    """
    Test methods defined on subscription
    """
    self._initSynchronization()
    self._initSyncModule()
    self.tic()
    # Init the sync
    nb_document=500
    self._fillModule(module=self.client_module, nb_objects=nb_document)
    self.tic()
    # Check the default getDocumentIdList behaviour
    r = self.sub.getDocumentIdList(limit=None)
    self.assertEqual(len(r), nb_document)
    # Now simulate the get and activate method
    # Test limit is well taken into account
    limit = 100
    r = self.sub.getDocumentIdList(limit=limit)
    self.assertEqual(len(r), limit)
    # Test the min_id parameter
    min_id = r[-1].getId()
    r = self.sub.getDocumentIdList(limit=None, min_id=min_id)
    self.assertEqual(len(r), nb_document-limit)
