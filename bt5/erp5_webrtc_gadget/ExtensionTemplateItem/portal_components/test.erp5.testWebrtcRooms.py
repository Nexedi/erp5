##############################################################################
#
# Copyright (c) 2002-2016 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
#from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestWebrtcRooms(SecurityTestCase):
  """
  Test Class to test webrtc rooms
  """

  def getTitle(self):
    return "SampleTest"

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    user_folder = self.getPortal().acl_users
    
    user_folder._doAddUser('anon_user', '', ['Anonymous',], [])
  
    #spy = dict(title='Anon User', reference='anon_user', function=None)
    #self.createSimpleUser(**spy)
    
    self.commit()
    self.tic()
    self.login('anon_user')
    self.webrtc_room_module = self.portal.getDefaultModule(portal_type='Webrtc Rooms Module')
    self.assertTrue(self.webrtc_room_module is not None)

  def _newRoom(self, title='test room'):
    """
    Function to create new room
    """
    return self.webrtc_room_module.WebrtcRoom_addWebrtcRoom(
      title=title,
      form_id='WebrtcRoomsModule_viewWebrtcRoomList',
      batch_mode=True
    )

  def _setOffer(self, roomid, peerid, data):
    """
    Function to create new offer
    """
    return self.webrtc_room_module.WebrtcRoom_storeOfferAnswer(
      roomid=roomid,
      peerid=peerid,
      data=data,
    )

  def _getOffer(self, roomid, name):
    """
    Function to get offer
    """
    return self.webrtc_room_module.WebrtcRoom_getOfferAnswer(
      roomid=roomid,
      name=name
    )

  def _getAllOffer(self, roomid):
    """
    Function to get all offers in room
    """
    return self.webrtc_room_module.WebrtcRoom_getAllOfferAnswer(
      roomid=roomid,
    )

  def _deleteOffer(self, roomid, name):
    """
    Function to delete offer
    """
    return self.webrtc_room_module.WebrtcRoom_deleteOfferAnswer(
      roomid=roomid,
      name=name
    )

  def test_00_AnonymousUserCanCreateRoom(self):
    self.assertUserCanAccessDocument('anon_user', self.webrtc_room_module)
    self.assertUserCanViewDocument('anon_user', self.webrtc_room_module)
    self.assertUserCanAddDocument('anon_user', self.webrtc_room_module)

    self.login('anon_user')
    
    room = self._newRoom(title='test_room0')
    self.tic()
    
    self.assertUserCanAccessDocument('anon_user', room)
    self.assertUserCanViewDocument('anon_user', room)
    self.assertUserCanAddDocument('anon_user', room)
    
    self.tic()
  
  def test_01_AnonymousUserCanAddAndGetOffer(self):
    self.login('anon_user')
    data = "{'type':'offer', 'data':'sdp:'v=0\r\n o=- 2708361213080913936 2 IN IP4 127.0.0.1\r\n\'}"
    roomid = 'test_room1'
    self._newRoom(title=roomid)
    setResponse = self._setOffer(roomid, 'master', data)
    self.assertEqual('ok', setResponse.body)
    self.tic()
  
    getResponse = self._getOffer(roomid, 'master')
    self.assertEqual(data, getResponse)
    self._deleteOffer(roomid, 'master')
    self.tic()

  def test_02_AnonymousUserCanGetAllOffer(self):
    self.login('anon_user')
    data = "{'type':'offer', 'data':'sdp:'v=0\r\n o=- 2708361213080913936 2 IN IP4 127.0.0.1\r\n\'}"
    roomid = 'test_room2'
    self._newRoom(title=roomid)
    self._setOffer(roomid, 'slave1', data)
    self._setOffer(roomid, 'slave2', data)
    
    getResponse = self._getAllOffer(roomid)
    self.assertEqual(['slave1', 'slave2'], getResponse)
    self._deleteOffer(roomid, 'slave1')
    self._deleteOffer(roomid, 'slave2')
    self.tic()
  
  def test_04_AnonymousUserCanDeleteOffer(self):
    self.login('anon_user')
    data = "{'type':'offer', 'data':'sdp:'v=0\r\n o=- 2708361213080913936 2 IN IP4 127.0.0.1\r\n\'}"
    roomid = 'test_room3'
    self._newRoom(title=roomid)
    self._setOffer(roomid, 'slave1', data)
    self._deleteOffer(roomid, 'slave1')
    try:
      self._getOffer(roomid, 'slave1')
    except KeyError:
      pass
    else:
      self.fail('No error was raised when getting a deleted key.')


