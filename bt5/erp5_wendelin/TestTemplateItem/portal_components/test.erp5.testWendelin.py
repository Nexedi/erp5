##############################################################################
#
# Copyright (c) 2002-2015 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime
import msgpack
import numpy as np
import string
import random

def getRandomString():
  return 'test_%s' %''.join([random.choice(string.ascii_letters + string.digits) \
    for n in xrange(32)])

class Test(ERP5TypeTestCase):
  """
  Wendelin Test
  """

  def getTitle(self):
    return "Wendelin Test"

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    # here, you can create the categories and objects your test will depend on
    pass

  def test_0_import(self): 		 
    """ 		 
    Test we can import certain libraries but still failure to do so should be a  		 
    a test step failure rather than global test failure. 		 
    """ 		 
    import scipy 		 
    import sklearn
    import pandas
    
  def test_01_IngestionFromFluentd(self):
    """
    Test ingestion using a POST Request containing a msgpack encoded message
    simulating input from fluentd
    """
    now = DateTime()
    portal = self.portal
    request = portal.REQUEST
    
    # simulate fluentd by setting proper values in REQUEST
    reference = getRandomString()
    request.method = 'POST'
    number_string = ','.join([str(x) for x in range(11)])
    number_string_list = [number_string]*10000
    real_data = '\n'.join(number_string_list)

    data_chunk = msgpack.packb([0, real_data], use_bin_type=True)
    request.set('reference', reference)
    request.set('data_chunk', data_chunk)
    
    # create ingestion policy
    ingestion_policy = portal.portal_ingestion_policies.newContent( \
      portal_type ='Ingestion Policy',
      reference = reference,
      version = '001',
      script_id = 'ERP5Site_handleDefaultFluentdIngestion')
    ingestion_policy.validate()
    
    # create sensor
    sensor = portal.sensor_module.newContent( \
                            portal_type='Sensor', 
                            reference = reference)
    sensor.validate()

    # create new Data Stream for test purposes
    data_stream = portal.data_stream_module.newContent( \
                   portal_type='Data Stream', \
                   reference=reference)
    data_stream.validate()
    
    # create Data Supply
    resource = portal.restrictedTraverse('data_product_module/wendelin_4')
    data_supply_kw = {'reference': reference,
                      'version': '001',
                      'start_date': now,
                      'stop_date': now + 365}
    data_supply_line_kw = {'resource_value': resource,
                           'source_section_value': sensor,
                           'destination_section_value': data_stream}
    data_supply = ingestion_policy.PortalIngestionPolicy_addDataSupply( \
                                      data_supply_kw, \
                                      data_supply_line_kw)
    self.tic()
    
    # do real ingestion call
    ingestion_policy.ingest()
    
    # ingestion handler script saves new data using new line so we 
    # need to remove it, it also stringifies thus we need to
    data_stream_data = data_stream.getData()
    self.assertEqual(real_data, data_stream_data)
    
    # try sample transformation
    reference = 'test-data-array- %s' %getRandomString()
    
    data_array = portal.data_array_module.newContent(
                                            portal_type='Data Array',
                                            reference = reference,
                                            version = '001')
    data_array.validate()
    self.tic()
    
    data_stream.DataStream_transform(\
        chunk_length = 5001, \
        transform_script_id = 'DataStream_copyCSVToDataArray',
        data_array_reference = reference)
    self.tic()
    
    # test some numpy operations
    zarray = data_array.getArray()
    np.average(zarray)
    # XXX: test that extracted array is same as input one
    self.assertNotEqual(None, zarray)
    
  def test_02_Examples(self):
    """
      Test we can use python scientific libraries by using directly created
      Wendelin examples.
    """
    portal = self.portal
    portal.game_of_life()
    # XXX: for now following ones are disabled as wendelin.core not available
    # in testnodes framework
    portal.game_of_life_out_of_core()
    portal.game_of_life_out_of_core_activities()
    
  def test_03_DataArray(self):
    """
      Test persistently saving a ZBig Array to a Data Array.
    """
    from wendelin.bigarray.array_zodb import ZBigArray
    
    data_array = self.portal.data_array_module.newContent( \
                   portal_type = 'Data Array')
    self.assertEqual(None, data_array.getArray())
    data_array.initArray((3, 3), np.uint8)
    self.tic()
    
    # test array stored and we return ZBig Array instance
    persistent_zbig_array = data_array.getArray()
    self.assertEqual(ZBigArray, persistent_zbig_array.__class__)
    
    # try to resize its numpy "view" and check that persistent one is not saved
    # as these are differerent objects
    pure_numpy_array = persistent_zbig_array[:,:] # ZBigArray -> ndarray view of it
    pure_numpy_array = np.resize(pure_numpy_array, (4, 4))
    self.assertNotEquals(pure_numpy_array.shape, persistent_zbig_array.shape)
    
    # test copy numpy -> wendelin but first resize persistent one (add new one)
    data_array.initArray((4, 4), np.uint8)
    persistent_zbig_array = data_array.getArray()
    new_array = np.arange(1,17).reshape((4,4))
    persistent_zbig_array[:,:] = new_array
    self.assertEquals(new_array.shape, persistent_zbig_array.shape)

    # (enable when new wendelin.core released as it can kill system)
    self.assertTrue(np.array_equal(new_array, persistent_zbig_array))
    
    # test set element in zbig array
    persistent_zbig_array[:2, 2] = 0
    self.assertFalse(np.array_equal(new_array, persistent_zbig_array))

    # resize Zbig Array (enable when new wendelin.core released as it can kill system)
    persistent_zbig_array = np.resize(persistent_zbig_array, (100,100))
    self.assertNotEquals(pure_numpy_array.shape, persistent_zbig_array.shape)