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
from wendelin.bigarray.array_zodb import ZBigArray
from cStringIO import StringIO
import msgpack
import numpy as np
import string
import random
import urllib

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

  def test_01_IngestionFromFluentd(self, old_fluentd=False):
    """
    Test ingestion using a POST Request containing a msgpack encoded message
    simulating input from fluentd.
    """
    portal = self.portal

    # add brand new ingestion
    reference = getRandomString()
    ingestion_policy, data_supply, data_product = portal.portal_ingestion_policies.IngestionPolicyTool_addIngestionPolicy(
      reference = reference, 
      title = reference, 
      batch_mode=1)
    self.tic()

    number_string_list = []
    for my_list in list(chunks(range(0, 100001), 10)):
      number_string_list.append(','.join([str(x) for x in my_list]))
    real_data = '\n'.join(number_string_list)
    # make sure real_data tail is also a full line
    real_data += '\n'

    # simulate fluentd
    body = msgpack.packb([0, real_data], use_bin_type=True)
    if old_fluentd:
      env = {'CONTENT_TYPE': 'application/x-www-form-urlencoded'}
      body = urllib.urlencode({'data_chunk': body})
    else:
      env = {'CONTENT_TYPE': 'application/octet-stream'}
    path = ingestion_policy.getPath() + '/ingest?reference=' + reference
    publish_kw = dict(user='ERP5TypeTestCase', env=env,
      request_method='POST', stdin=StringIO(body))
    response = self.publish(path, **publish_kw)
    # Due to inconsistencies in the Zope framework,
    # a normal instance returns 204. As explained at
    # http://blog.ploeh.dk/2013/04/30/rest-lesson-learned-avoid-204-responses/
    # turning 200 into 204 automatically when the body is empty is questionable.
    self.assertEqual(200, response.getStatus())

    # at every ingestion if no specialised Data Ingestion exists it is created
    # thus it is needed to wait for server side activities to be processed
    self.tic()

    # get related Data ingestion
    data_ingestion = data_supply.Base_getRelatedObjectList(portal_type='Data Ingestion')[0]
    self.assertNotEqual(None, data_ingestion)
    data_ingestion_line = [x for x in data_ingestion.objectValues() if x.getReference() == 'out_stream'][0]

    data_stream = data_ingestion_line.getAggregateValue()
    self.assertEqual('Data Stream', data_stream.getPortalType())

    data_stream_data = data_stream.getData()
    self.assertEqual(real_data, data_stream_data)

    # try sample transformation
    data_array = portal.data_array_module.newContent(
                          portal_type = 'Data Array', 
                          reference = reference)
    data_array.validate()
    self.tic()

    data_stream.DataStream_transform(\
        chunk_length = 10450, \
        transform_script_id = 'DataStream_copyCSVToDataArray',
        data_array_reference = reference)
    self.tic()

    # test that extracted array contains same values as input CSV
    zarray = data_array.getArray()
    self.assertEqual(np.average(zarray), np.average(np.arange(100001)))
    self.assertTrue(np.array_equal(zarray, np.arange(100001)))

    # clean up
    data_array.invalidate()
    data_stream.setData('')
    self.tic()


  def test_01_1_IngestionFromOldFluentd(self):
    self.test_01_IngestionFromFluentd(True)

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

    data_stream = portal.data_stream_module.newContent(
                    portal_type = 'Data Stream',
                    reference = reference)
    data_stream.appendData(real_data)
    data_stream.validate()
    data_array = portal.data_array_module.newContent(
                          portal_type = 'Data Array', 
                          reference = reference)
    data_array.validate()
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

  def test_04_DataBucket(self):
    """
      Test data bucket
    """
    bucket_stream = self.portal.data_stream_module.newContent( \
                                portal_type = 'Data Bucket Stream')
    self.tic()
    
    self.assertEqual(0, len(bucket_stream))
    
    # test set and get
    bin_string = "1"*100000
    key = len(bucket_stream) + 1
    bucket_stream.insertBucket(key, bin_string )
    self.assertEqual(bin_string, bucket_stream.getBucketByKey(key))
    
    # test sequence
    self.assertEqual(1, len(bucket_stream))
    
    # test delete bucket by key
    bucket_stream.delBucketByKey(key)
    self.assertEqual(0, len(bucket_stream))
    
    # set many buckets
    for i in range(100):
      bucket_stream.insertBucket(i, i*10000)

    self.assertEqual(100, len(bucket_stream))
    self.assertEqual(range(100), bucket_stream.getKeyList())
    
    # test as sequence
    bucket = bucket_stream.getBucketKeyItemSequenceByKey(start_key=10, count=1)[0]
    self.assertEqual(100000, bucket[1].value)

  def test_05_DataAnalyses(self):
    """
      Test data analyses' default configuration.
      By default we have no Data Analyses configured thus test is minimal.
    """
    self.portal.Alarm_handleAnalysis()
    self.tic()

  def test_06_DefaultWendelinConfigurationExistency(self):
    """
      Test that nobody accidently removes needed by HowTo's default configurations.
    """
    # the default json ingestion is usde in HowTo/ Docs
    self.assertNotEqual(None, 
           getattr(self.portal.portal_ingestion_policies, "default_http_json", None))
    self.assertNotEqual(None, 
           getattr(self.portal.data_supply_module, "default_http_json", None))
