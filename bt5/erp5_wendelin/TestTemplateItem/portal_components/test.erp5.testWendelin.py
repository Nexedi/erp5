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
from Products.ERP5Type.tests.utils import createZODBPythonScript
from wendelin.bigarray.array_zodb import ZBigArray
from zExceptions import NotFound
import msgpack
import numpy as np
import string
import random

def getRandomString():
  return 'test_%s' %''.join([random.choice(string.ascii_letters + string.digits) \
    for _ in xrange(32)])
    
def chunks(l, n):
  """Yield successive n-sized chunks from l."""
  for i in xrange(0, len(l), n):
    yield l[i:i+n]

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
  
  def stepSetupIngestion(self, reference):
    """
      Generic step.
    """
    ingestion_policy, data_supply, data_stream, data_array = \
      self.portal.portal_ingestion_policies.IngestionPolicyTool_addIngestionPolicy( \
        reference  = reference, \
        batch_mode = 1)
    self.tic()
    
    return ingestion_policy, data_supply, data_stream, data_array
    
   
  def test_0_import(self): 		 
    """ 		 
    Test we can import certain libraries but still failure to do so should be a  		 
    a test step failure rather than global test failure. 		 
    """ 		 
    import scipy as _	 
    import sklearn as _
    import pandas as _
    import matplotlib as _

  def test_01_IngestionFromFluentd(self):
    """
    Test ingestion using a POST Request containing a msgpack encoded message
    simulating input from fluentd.
    """
    portal = self.portal
    request = portal.REQUEST
    
    reference = getRandomString()
    number_string_list = []
    for my_list in list(chunks(range(0, 100001), 10)):
      number_string_list.append(','.join([str(x) for x in my_list]))
    real_data = '\n'.join(number_string_list)
    # make sure real_data tail is also a full line
    real_data += '\n'

    ingestion_policy, _, data_stream, data_array = \
      self.stepSetupIngestion(reference)
    
    # simulate fluentd by setting proper values in REQUEST
    request.method = 'POST'
    data_chunk = msgpack.packb([0, real_data], use_bin_type=True)
    request.set('reference', reference)
    request.set('data_chunk', data_chunk)
    ingestion_policy.ingest()
    
    data_stream_data = data_stream.getData()
    self.assertEqual(real_data, data_stream_data)
    
    # try sample transformation
    data_stream.DataStream_transform(\
        chunk_length = 10450, \
        transform_script_id = 'DataStream_copyCSVToDataArray',
        data_array_reference = reference)

    self.tic()
    
    # test that extracted array contains same values as input CSV
    zarray = data_array.getArray()
    self.assertEqual(np.average(zarray), np.average(np.arange(100001)))
    self.assertTrue(np.array_equal(zarray, np.arange(100001)))
    
    # test ingesting with bad reference and raise of NotFound
    request.set('reference', reference + 'not_existing')
    self.assertRaises(NotFound, ingestion_policy.ingest)
    
    
  def test_01_1_IngestionTail(self):
    """
    Test real time convertion to a numpy array by appending data to a data stream.
    """
    portal = self.portal

    reference = getRandomString()
    number_string_list = []
    for my_list in list(chunks(range(0, 10001), 10)):
      number_string_list.append(','.join([str(x) for x in my_list]))
    real_data = '\n'.join(number_string_list)
    # make sure real_data tail is also a full line
    real_data += '\n'

    _, _, data_stream, data_array = self.stepSetupIngestion(reference)
    data_stream.appendData(real_data)
    self.tic()
    
    self.assertEqual(None, data_array.getArray())

    # override DataStream_transformTail to actually do transformation on appenData
    start = data_stream.getSize()
    script_id = 'DataStream_transformTail'
    script_content_list = ["start_offset, end_offset", """
# created by testWendelin.test_01_1_IngestionTail
start = %s
end  = %s
context.activate().DataStream_readChunkListAndTransform( \
  start, \
  end, \
  %s, \
  transform_script_id = 'DataStream_copyCSVToDataArray', \
  data_array_reference=context.getReference())""" %(start, start + 10450, 10450)]
    createZODBPythonScript(
      portal.portal_skins.custom, 
      script_id, 
      *script_content_list)
    
    number_string_list = []
    for my_list in list(chunks(range(10001, 200001), 10)):
      number_string_list.append(','.join([str(x) for x in my_list]))
    real_data = '\n'.join(number_string_list)
    # make sure real_data tail is also a full line
    real_data += '\n'
      
    # append data to Data Stream and check array which should be feed now.
    data_stream.appendData(real_data)
    self.tic()
    
    # test that extracted array contains same values as input CSV
    zarray = data_array.getArray()
    expected_numpy_array = np.arange(10001, 200001)
    self.assertEqual(np.average(zarray), np.average(expected_numpy_array))
    self.assertTrue(np.array_equal(zarray, expected_numpy_array))
    
    # clean up script
    portal.portal_skins.custom.manage_delObjects([script_id,])
    self.tic()
    
    # analyze numpy array using activities.
    active_process = portal.portal_activities.newActiveProcess()
    zarray = data_array.getArray()
    max_elements = zarray.shape[0]
    expected_result_list = []
    jobs = 15
    offset = max_elements / jobs
    start = 0
    end = start + offset
    for _ in range(jobs):
      # calculate directly expectations
      expected_result_list.append(np.average(expected_numpy_array[start:end]))
      data_array.activate(
                   active_process = active_process.getPath(),  \
                   activity='SQLQueue').DataArray_calculateArraySliceAverageAndStore(start, end)
      data_array.log('%s %s' %(start, end))
      start += offset
      end += offset
    self.tic()
    
    result_list = [x.getResult() for x in active_process.getResultList()]
    self.assertSameSet(result_list, expected_result_list)
    # final reduce job to a number
    sum(result_list)

  def test_01_02_ParallelTransformation(self):
    """
    test parallel execution.
    Note: determining row length is important in this case
    """
    portal = self.portal
    reference = getRandomString()
    
    row = ','.join(['%s' %x for x in range(1000)])
    number_string_list = [row]*20
    real_data = '\n'.join(number_string_list)

    portal.log( real_data)
    
    _, _, data_stream, _ = self.stepSetupIngestion(reference)
    data_stream.appendData(real_data)
    self.tic()
    
    data_stream.DataStream_transform(\
        chunk_length = len(row), \
        transform_script_id = 'DataStream_copyCSVToDataArray',
        data_array_reference = reference,
        parallelize = 1)

    self.tic()


  def test_02_Examples(self):
    """
      Test we can use python scientific libraries by using directly created
      Wendelin examples.
    """
    portal = self.portal
    portal.game_of_life()
    portal.game_of_life_out_of_core()
    portal.game_of_life_out_of_core_activities()
    
  def test_03_DataArray(self):
    """
      Test persistently saving a ZBig Array to a Data Array.
    """
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
    self.assertTrue(np.array_equal(new_array, persistent_zbig_array))
    
    # test set element in zbig array
    persistent_zbig_array[:2, 2] = 0
    self.assertFalse(np.array_equal(new_array, persistent_zbig_array))

    # resize Zbig Array
    persistent_zbig_array = np.resize(persistent_zbig_array, (100,100))
    self.assertNotEquals(pure_numpy_array.shape, persistent_zbig_array.shape)
    
    # get array slice (fails)
    data_array = self.portal.data_array_module.newContent( \
                   portal_type = 'Data Array')
    shape = (1000,)
    data_array.initArray(shape, np.uint8)
    self.tic()
    
    persistent_zbig_array = data_array.getArray()
    new_array = np.arange(1000)
    new_array.resize(shape)

    self.assertEquals(new_array.shape, persistent_zbig_array.shape)
        
    persistent_zbig_array[:,] = new_array
    self.tic()

    self.assertTrue(
           np.array_equal(data_array.getArraySlice(0,100), \
                          new_array[:100]))
    