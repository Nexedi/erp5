##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                     Ivan Tyagov <ivan@nexedi.com>
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
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.Tool.SessionTool import SESSION_CACHE_FACTORY
from string import letters as LETTERS
from random import choice
import time

primitives_kw = dict(attr_1 = ['list_item'], \
                     attr_2 = ('tuple1','tuple2',), \
                     attr_3 = 1, \
                     attr_4 = 0.1, \
                     attr_5 = {'some_key':  'some_value'}, \
                     attr_6 = 'string', )

class TestSessionTool(ERP5TypeTestCase):

  session_id = "123456789"

  def getTitle(self):
    return "Session Tool"

  def afterSetUp(self):
    # create a Memcached Plugin
    memcached_tool = self.portal.portal_memcached
    #create Memcache Plugin
    if getattr(memcached_tool, 'default_memcached_plugin', None) is None:
      memcached_tool.newContent(id='default_memcached_plugin',
                                portal_type='Memcached Plugin',
                                int_index=0,
                                url_string='127.0.0.1:11211')
    self.login()

  def login(self):
    uf = self.portal.acl_users
    uf._doAddUser('ivan', '', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('ivan').__of__(uf)
    newSecurityManager(None, user)

  def _changeCachePlugin(self, portal_type, storage_duration = 86400):
    """ Change current cache plugin with new one. """
    portal_caches = self.portal.portal_caches
    session_cache_factory = getattr(portal_caches, SESSION_CACHE_FACTORY)
    # remove current cache plugin
    session_cache_factory.manage_delObjects(list(session_cache_factory.objectIds()))
    cache_plugin = session_cache_factory.newContent(portal_type=portal_type)
    cache_plugin.setCacheDuration(storage_duration)
    cache_plugin.setIntIndex(0)
    if portal_type == 'Distributed Ram Cache':
      cache_plugin.edit(specialise='portal_memcached/default_memcached_plugin')
    self.commit()
    portal_caches.updateCache()

  def stepTestSetGet(self, sequence=None,
                     sequence_list=None, **kw):
    session = self.portal.portal_sessions[self.session_id]
    session.clear()
    session.update(primitives_kw)
    session = self.portal.portal_sessions[self.session_id]
    self.assertEqual(primitives_kw, session)

    # API check
    self.assert_(self.portal.portal_sessions[self.session_id] ==  \
                   self.portal.portal_sessions.getSession(self.session_id))
    session.clear()
    session.edit(**primitives_kw)
    session = self.portal.portal_sessions[self.session_id]
    self.assertEqual(primitives_kw, session)

  def stepTestAcquisitionRamSessionStorage(self, sequence=None, \
                                           sequence_list=None, **kw):
    portal_sessions =  self.portal.portal_sessions
    session = portal_sessions.newContent(
                      self.session_id,
                      attr_1=self.portal.newContent(temp_object=True, portal_type='Document', id='1'),
                      attr_2=self.portal.newContent(temp_object=True, portal_type='Document', id='2'))
    ## check temp (RAM based) attributes stored in session
    for i in range (1, 3):
      attr_name = 'attr_%s' %i
      self.assert_(attr_name in session.keys())
      attr = session[attr_name]
      self.assert_(str(i), attr.getId())
      self.assert_(0 == len(attr.objectIds()))

  def stepModifySession(self, sequence=None, \
                        sequence_list=None, **kw):
    """ Modify session and check that modifications are updated in storage backend."""
    portal_sessions = self.portal.portal_sessions
    session = portal_sessions.newContent(self.session_id, \
                                         **primitives_kw)
    session = portal_sessions[self.session_id]
    session.pop('attr_1')
    del session['attr_2']

    # get again session object again and check that session value is updated
    # (this makes sense for memcached)
    session = portal_sessions[self.session_id]
    self.assert_(not 'attr_1' in session.keys())
    self.assert_(not 'attr_2' in session.keys())

    session.update(**{'key_1':'value_1',
                      'key_2':'value_2',})
    session = portal_sessions[self.session_id]
    self.assert_('key_1' in session.keys())
    self.assert_(session['key_1'] == 'value_1')
    self.assert_('key_2' in session.keys())
    self.assert_(session['key_2'] == 'value_2')

    session.clear()
    session = portal_sessions[self.session_id]
    self.assert_(session == {})

    session['pop_key'] = 'pop_value'
    session = portal_sessions[self.session_id]
    self.assert_(session['pop_key'] == 'pop_value')
    session.popitem()
    session = portal_sessions[self.session_id]
    self.assert_(session == {})

    session.setdefault('default', 'value')
    session = portal_sessions[self.session_id]
    self.assert_(session['default'] == 'value')

  def stepDeleteClearSession(self, sequence=None, \
                             sequence_list=None, **kw):
    """ Get session object and check keys stored in previous test. """
    portal_sessions =  self.portal.portal_sessions
    session = portal_sessions.newContent(self.session_id, \
                                         **primitives_kw)
    # delete it
    portal_sessions.manage_delObjects(self.session_id)
    session = portal_sessions[self.session_id]
    self.assert_({} == session)
    # clear it
    session = portal_sessions.newContent(
                      self.session_id, \
                      **primitives_kw)
    session = portal_sessions[self.session_id]
    self.assert_(primitives_kw == session)
    session.clear()
    session = portal_sessions[self.session_id]
    self.assert_(session == {})

  def stepTestSessionDictInterface(self, sequence=None, \
                                   sequence_list=None, **kw):
    session = self.portal.portal_sessions[self.session_id]
    session.clear()
    # get / set
    session['foo'] = 'Bar'
    self.assertTrue('foo' in session)
    self.assertEqual('Bar', session['foo'])
    self.assertEqual('Bar', session.get('foo'))
    self.assertFalse('bar' in session)
    self.assertEqual('Default', session.get('bar', 'Default'))
    self.assertRaises(KeyError, session.__getitem__, 'bar')

    # pop
    session['pop'] = 'Bar'
    self.assertEqual('Bar', session.pop('pop'))
    self.assertRaises(KeyError, session.__getitem__, 'pop')
    self.assertEqual('Default', session.pop('pop', 'Default'))

    # setdefault
    self.assertEqual('Default', session.setdefault('setdefault', 'Default'))
    self.assertEqual('Default', session.setdefault('setdefault', 'Default was set'))

    # clear / items
    session.clear()
    self.assertEqual([], list(session.items()))

    # popitem
    session['popitem'] = 'Bar'
    self.assertEqual(('popitem', 'Bar'), session.popitem())
    self.assertRaises(KeyError, session.popitem)


  def stepTestSessionGetattr(self, sequence=None, \
                             sequence_list=None, **kw):
    session = self.portal.portal_sessions[self.session_id]
    session.clear()
    session['foo'] = 'Bar'
    #self.assertEqual('Bar', session.foo)
    self.assertEqual('Default', getattr(session, 'bar', 'Default'))
    self.assertRaises(AttributeError, getattr, session, 'bar')

  def stepTestSessionBulkStorage(self, sequence=None, \
                                 sequence_list=None, **kw):
    """ Test massive session sets which uses different cache plugin. """
    kw = {}
    session = self.portal.portal_sessions[self.session_id]
    session.clear()
    session = self.portal.portal_sessions[self.session_id]

    # test many sets
    for i in range(0, 500):
      v = ''.join([choice(LETTERS) for _ in range(10)])
      session[i] = v
      kw[i] = v
    session = self.portal.portal_sessions[self.session_id]
    self.assertEqual(kw, session)

    # test big session
    session.clear()
    for key in kw.keys():
      kw[key] = ''.join([choice(LETTERS) for _ in range(1000)])
    session.update(kw)
    session = self.portal.portal_sessions[self.session_id]
    self.assertEqual(kw, session)

  def stepTestSessionExpire(self, sequence=None, \
                            sequence_list=None, **kw):
    """ Test expire session which uses different cache plugin. """
    interval = 3
    portal_sessions = self.portal.portal_sessions
    portal_sessions.manage_delObjects(self.session_id)
    session = portal_sessions.getSession(self.session_id, session_duration = interval)
    session['key'] = 'value'
    time.sleep(interval+1)
    session = self.portal.portal_sessions.getSession(self.session_id)
    # session should be an emty dic as it expired
    self.assert_(session == {})

  def stepTestCheckSessionAfterNewPerson(self, sequence=None, \
                                  sequence_list=None, **kw):
    """ Test if session still the same after create new person setting the
    reference. """
    session = self.portal.portal_sessions[self.session_id]
    session.clear()
    session['key'] = 'value'

    self.portal.person_module.newContent(portal_type='Person',
                                        default_address_city='test',
                                        default_address_region='test',
                                        default_address_street_address='test',
                                        default_email_text='test@test.com',
                                        default_fax_text='123456789',
                                        first_name='test',
                                        last_name='test',
                                        password='secret',
                                        reference='test')

    session = self.portal.portal_sessions[self.session_id]
    self.assertEqual(session.get('key'),  'value')
    self.abort()

  def test_01_CheckSessionTool(self):
    """ Checks session tool is present """
    self.assertNotEqual(None, getattr(self.portal, 'portal_sessions', None))

  def test_02_RamSession(self):
    """ Test RamSession which uses local RAM based cache plugin. """
    sequence_list = SequenceList()
    sequence_string =  'stepTestSetGet  \
                    stepTestAcquisitionRamSessionStorage \
                    stepModifySession  \
                    stepDeleteClearSession \
                    stepTestSessionDictInterface \
                    stepTestSessionGetattr  \
                    stepTestSessionBulkStorage  \
                    stepTestSessionExpire  \
                    stepTestCheckSessionAfterNewPerson \
                    '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_03_MemcachedDistributedSession(self):
    """ Test DistributedSession which uses memcached based cache plugin. """
    # create memcached plugin and test
    self._changeCachePlugin('Distributed Ram Cache')
    sequence_list = SequenceList()
    sequence_string =  'stepTestSetGet  \
                        stepModifySession  \
                        stepDeleteClearSession \
                        stepTestSessionDictInterface \
                        stepTestSessionGetattr  \
                        stepTestSessionBulkStorage  \
                        stepTestSessionExpire  \
                        stepTestCheckSessionAfterNewPerson \
                   '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSessionTool))
  return suite
