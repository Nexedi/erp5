##############################################################################
#
# Copyright (c) 2002-2015 Nexedi SA and Contributors. All Rights Reserved.
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.
#
##############################################################################

from cStringIO import StringIO
import base64
import binascii
from httplib import NO_CONTENT
import msgpack
import numpy as np
import string
import random
import struct
import textwrap
import urllib
import uuid
from zExceptions import BadRequest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript, removeZODBPythonScript
from wendelin.bigarray.array_zodb import ZBigArray

from App.version_txt import getZopeVersion
if getZopeVersion() < (4, ): # BBB Zope2
  # Zope set http status code 204 for empty response, but
  # on Zope 2 this is not correctly reflected in ERP5TypeTestCase.publish,
  # for such responses the status is set to 200 (but for "real" requests
  # it is set to 204, this only affected the testing)
  NO_CONTENT = 200


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

  def createAndRunScript(self, code, expected=None):
    # we do not care the script name for security test thus use uuid1
    name = str(uuid.uuid1())
    script_container = self.portal.portal_skins.custom
    try:
      createZODBPythonScript(script_container, name, '**kw', textwrap.dedent(code))
      self.assertEqual(getattr(self.portal, name)(), expected)
    finally:
      removeZODBPythonScript(script_container, name)

  def test_01_IngestionFromFluentd(self, old_fluentd=False):
    """
    Test ingestion using a POST Request containing a msgpack encoded message
    simulating input from fluentd.
    """
    portal = self.portal

    # add brand new ingestion
    reference = getRandomString()
    ingestion_policy, data_supply, _ = portal.portal_ingestion_policies.IngestionPolicyTool_addIngestionPolicy(
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
    self.assertEqual(NO_CONTENT, response.getStatus())
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
    data_stream.setData(None)
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
    self.assertEqual(bin_string, bucket_stream.getBucketByIndex(0))

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
    # the default json ingestion is used in HowTo / Docs
    self.assertNotEqual(None,
           getattr(self.portal.portal_ingestion_policies, "default", None))
    self.assertNotEqual(None,
           getattr(self.portal.data_supply_module, "default", None))

  def test_07_LinkedDataStreamList(self):
    """
      Test linked Data Streams
    """
    data_stream_1 = self.portal.data_stream_module.newContent(title = "Data Stream 1", \
                                                              portal_type = "Data Stream")
    data_stream_2 = self.portal.data_stream_module.newContent(title = "Data Stream 2", \
                                                              portal_type = "Data Stream")
    data_stream_3 = self.portal.data_stream_module.newContent(title = "Data Stream 3", \
                                                              portal_type = "Data Stream")
    data_stream_4 = self.portal.data_stream_module.newContent(title = "Data Stream 4", \
                                                              portal_type = "Data Stream")
    data_stream_5 = self.portal.data_stream_module.newContent(title = "Data Stream 5", \
                                                              portal_type = "Data Stream")

    # test nothing linked
    self.assertSameSet([], data_stream_2.getRecursiveSuccessorValueList())
    self.assertSameSet([], data_stream_2.getRecursivePredecessorValueList())

    # set linked data streams (1 <--> 2 <--> 3 <--> 4 <--> 5)
    data_stream_1.setSuccessorValue(data_stream_2)
    data_stream_2.setSuccessorValue(data_stream_3)
    data_stream_3.setSuccessorValue(data_stream_4)
    data_stream_4.setSuccessorValue(data_stream_5)

    # set predecessor
    data_stream_2.setPredecessorValue(data_stream_1)
    data_stream_3.setPredecessorValue(data_stream_2)
    data_stream_4.setPredecessorValue(data_stream_3)
    data_stream_5.setPredecessorValue(data_stream_4)

    # test successor
    self.assertSameSet(data_stream_2.getRecursiveSuccessorValueList(), \
                       [data_stream_3, data_stream_4, data_stream_5])
    self.assertSameSet(data_stream_5.getRecursiveSuccessorValueList(), \
                       [])

    # test predecessor
    self.assertSameSet(data_stream_1.getRecursivePredecessorValueList(), \
                       [])
    self.assertSameSet(data_stream_2.getRecursivePredecessorValueList(), \
                       [data_stream_1])
    self.assertSameSet(data_stream_5.getRecursivePredecessorValueList(), \
                       [data_stream_4, data_stream_3, data_stream_2, data_stream_1])

  def test_08_ImportSklearn(self):
    """
      Test import of Scikit-learn and minimal example of usage.
    """

    from sklearn.linear_model import LinearRegression
    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])

    # y = 1 * x_0 + 2 * x_1 + 3
    y = np.dot(X, np.array([1, 2])) + 3

    reg = LinearRegression().fit(X, y)
    predicted = reg.predict(np.array([[4, 10]]))
    self.assertEqual(predicted.all(),np.array([27.]).all())

  def test_09_IngestionFromFluentdStoreMsgpack(self, old_fluentd=False):
    """
    Test ingestion using a POST Request containing a msgpack encoded message
    simulating input from fluentd.
    """
    from datetime import datetime
    import time

    portal = self.portal
    now = datetime.now()

    reference="test_sensor.test_product"
    ingestion_policy = portal.portal_ingestion_policies['default']
    data_supply = portal.data_supply_module["default"]

    data_list = []
    int_date = int(time.mktime(now.timetuple()))
    real_data = []

    # create data for ingestion in [date, value]  format
    for x in range(0, 10001):
      data_list = []
      data_list = [int_date, x]
      real_data.append(data_list)
      int_date = int_date + 1000

    # simulate fluentd
    body = msgpack.packb(real_data, use_bin_type=True)
    env = {'CONTENT_TYPE': 'application/octet-stream'}

    path = ingestion_policy.getPath() + '/ingest?reference=' + reference
    publish_kw = dict(user='ERP5TypeTestCase', env=env,
      request_method='POST', stdin=StringIO(body))
    response = self.publish(path, **publish_kw)

    self.assertEqual(NO_CONTENT, response.getStatus())

    self.tic()

    # get related Data ingestion
    data_ingestion = data_supply.Base_getRelatedObjectList(portal_type='Data Ingestion')[0]
    self.assertNotEqual(None, data_ingestion)
    data_ingestion_line = [x for x in data_ingestion.objectValues() if x.getReference() == 'out_stream'][0]

    data_stream = data_ingestion_line.getAggregateValue()
    self.assertEqual('Data Stream', data_stream.getPortalType())

    data_stream_data = data_stream.getData()
    # body is msgpacked real data.
    self.assertEqual(body, data_stream_data)

    # unpack data
    start = 0
    end = len(data_stream_data)
    unpacked, end = data_stream.readMsgpackChunkList(start, end)
    # compare unpacked data with real data
    self.assertEqual([real_data], unpacked)

    # extract dates and compare with real dates
    f = data_stream.extractDateTime
    for i in range(0, len(unpacked[0])):
      self.assertEqual(np.datetime64(real_data[i][0], 's'), f(unpacked[0][i][0]))

    # clean up
    data_stream.setData(None)
    self.tic()

  def _removeDocument(self, document_to_remove):
    path = document_to_remove.getRelativeUrl()
    container, _, object_id = path.rpartition('/')
    parent = self.portal.unrestrictedTraverse(container)
    parent.manage_delObjects([object_id])
    self.commit()

  def _addDataIngestionToDataSupply(self, data_supply):
    portal = self.portal

    data_supply_line = data_supply.objectValues()[0]
    data_ingestion = portal.data_ingestion_module.newContent(
      portal_type="Data Ingestion",
      title="TestDI_%s" % data_supply.getTitle(),
      reference="Test_DI_%s" % data_supply.getTitle(),
      specialise=data_supply.getRelativeUrl(),
      source=data_supply.getSource(),
      source_section=data_supply.getSourceSection(),
      destination="organisation_module/test_wendelin_destination",
      destination_section="organisation_module/test_wendelin_destination_section",
      start_date=data_supply.getCreationDate())

    self.addCleanup(self._removeDocument, data_ingestion)

    data_ingestion.newContent(
      portal_type="Data Ingestion Line",
      title="Ingest Data",
      reference="ingestion_operation",
      aggregate=data_supply_line.getSource(),
      resource="data_operation_module/wendelin_ingest_data",
      int_index=1
    )

    data_ingestion.newContent(
      portal_type="Data Ingestion Line",
      title="test_wendelin_data_product",
      reference="out_stream",
      aggregate_list=[data_supply_line.getSource(), data_supply_line.getDestination()],
      resource="data_product_module/test_wendelin_data_product",
      use="use/big_data/ingestion/stream",
      quantity=1,
      int_index=2
    )

    data_ingestion.start()

    return data_ingestion

  def test_10_DataAnalysesCreation(self):
    """
    Test data ingestion and analyses execution.
    """
    portal = self.portal

    # test DataSupply_viewAddRelatedDataIngestionActionDialog dialog
    # this test code will create a Data Ingestion which itself will
    # be used in later tests of ERP5Site_createDataAnalysisList
    data_supply = portal.data_supply_module.test_10_DataAnalysesCreation_data_supply
    data_ingestion = self._addDataIngestionToDataSupply(data_supply)

    self.assertNotEqual(None, data_ingestion)
    self.tic()

    before_data_analysis_list = portal.portal_catalog(
      portal_type = "Data Analysis",
      simulation_state = "started")

    # create DA from DI
    portal.ERP5Site_createDataAnalysisList()
    self.tic()

    # check new three Data Arrays created
    after_data_analysis_list = portal.portal_catalog(
      portal_type = "Data Analysis",
      simulation_state = "started")

    before_data_analysis_list = set([x.getObject() for x in before_data_analysis_list])
    after_data_analysis_list = set([x.getObject() for x in after_data_analysis_list])
    self.assertEqual(1, len(after_data_analysis_list) - len(before_data_analysis_list))

    # check properly created
    to_delete_data_analysis = after_data_analysis_list - before_data_analysis_list

    for data_analysis in list(to_delete_data_analysis):
      if data_ingestion == data_analysis.getCausalityValue():
        to_delete_data_analysis = data_analysis
        break

    self.addCleanup(self._removeDocument, to_delete_data_analysis)

    data_transformation = portal.data_transformation_module.test_wendelin_data_transformation

    self.assertEqual(data_ingestion, to_delete_data_analysis.getCausalityValue())
    self.assertSameSet(
      [data_supply, data_transformation],
      to_delete_data_analysis.getSpecialiseValueList()
    )
    # all lines should be properly created
    self.assertEqual(len(data_transformation.objectValues()),
                     len(to_delete_data_analysis.objectValues()))
    self.assertEqual("started", to_delete_data_analysis.getSimulationState())

  def test_11_temporaryDataArray(self):
    """
      Test if temporary Data Array is functional.
    """
    portal = self.portal
    ndarray = np.array([[0, 1], [2, 3]])
    temporary_data_array = portal.data_array_module.newContent(
      portal_type='Data Array',
      temp_object=True
    )
    zbigarray = temporary_data_array.initArray(shape=ndarray.shape, dtype=ndarray.dtype)
    zbigarray.append(ndarray)
    self.assertTrue(np.array_equal(zbigarray[2:], ndarray))

  def test_12_numpyWendelinConversion(self):
    """
      Test if conversion from numpy arrays to wendelin data works.
    """
    portal = self.portal
    ndarray = np.array([[0, 1], [2, 3]])
    wendelin_data = portal.Base_numpyToWendelinData(ndarray)
    reconverted_ndarray = portal.Base_wendelinDataToNumpy(wendelin_data)

    self.assertIsInstance(wendelin_data, bytes)

    # Check for header
    self.assertEqual(wendelin_data[:4], b'\x92WEN')

    # Test checksum
    checksum = struct.unpack('<i', wendelin_data[6:10])[0]
    self.assertEqual(checksum, binascii.crc32(wendelin_data[10:]))

    # Test inverse conversion works
    self.assertTrue(np.array_equal(ndarray, reconverted_ndarray))

    self.assertTrue(
      np.array_equal(
        portal.Base_wendelinTextToNumpy(
          "kldFTgABq96QqZNOVU1QWQEARgB7J2Rlc2NyJzogJzxmOCcsICdmb3J0cmFuX29yZGVyJzogRmFsc2UsICdzaGFwZSc6ICgwLCksIH0gICAgICAgICAgICAK="
        ),
        np.array([]),
      )
    )

  def test_13_unpackLazy(self):
    """
      Ensure unpackLazy is available and functional in restricted python
    """
    ingestion_policy_id = "test_13_unpackLazy_IngestionPolicy"
    try:
      ingestion_policy = self.getPortal().portal_ingestion_policies.newContent(
        id=ingestion_policy_id,
        title=ingestion_policy_id,
        portal_type='Ingestion Policy',
        reference=ingestion_policy_id,
        version = '001',
      )
    # ingestion_policy still exists from previous failed test run
    except BadRequest:
      ingestion_policy = self.portal.get(ingestion_policy_id)

    self.assertNotEqual(ingestion_policy, None)

    self.tic()

    self.addCleanup(self._removeDocument, ingestion_policy)

    code = r"""
ingestion_policy = context.portal_ingestion_policies.get("{}")
result = [x for x in ingestion_policy.unpackLazy('b"\x93\x01\x02\x03"')]
return result
""".format(ingestion_policy_id)

    self.createAndRunScript(code, [98, 34, [1, 2, 3], 34])

  def test_14_IndexSequenceInRestrictedPython(self):
    """
      Ensure its possible to iterate over return values of DataBucketStream methods
      in restricted python.
    """

    code = r"""
data_bucket_stream = context.portal_catalog.data_stream_module.newContent(
  portal_type='Data Bucket Stream'
)
data_bucket_stream.insertBucket(1,  "1" * 100000)
result = [x for x in data_bucket_stream.getBucketIndexKeySequenceByIndex()]
"""

    self.createAndRunScript(code)

  def test_15_setArrayDtypeNames(self):
    """
      Test Data Array method "setArrayDtypeNames"
    """
    data_array = self.portal.data_array_module.newContent(
      portal_type="Data Array"
    )
    self.addCleanup(self._removeDocument, data_array)
    dtype_name0, dtype_name1 = "my_dtype_name", "my_new_dtype_name"
    data_array.initArray((3,), np.dtype([(dtype_name0, np.float64)]))
    self.assertEqual(data_array.getArrayDtypeNames(), (dtype_name0,))
    data_array.setArrayDtypeNames((dtype_name1,))
    self.assertEqual(data_array.getArrayDtypeNames(), (dtype_name1,))

  def test_16_createDataAnalysisFromDataTransformationWithoutResolution(self):
    """
      Ensure data analysis are created from data transformation without any specified
      variation categories.
    """
    portal = self.portal
    title_prefix = "Wendelin Test 16"

    test_function_to_organisation = {}
    for test_function in ("source", "destination"):
      organisation = portal.organisation_module.newContent(
        portal_typle="Organisation",
        title="%s %s" % (title_prefix, test_function),
      )
      self.addCleanup(self._removeDocument, organisation)
      organisation.validate()
      test_function_to_organisation.update({test_function: organisation})

    data_operation = portal.data_operation_module.newContent(
      portal_typle="Data Operation",
      title="%s Data Operation" % title_prefix,
      script_id="DataAnalysisLine_testWendelinConvertAToB",
    )
    self.addCleanup(self._removeDocument, data_operation)
    data_operation.validate()

    resource = portal.data_product_module.newContent(
      portal_type="Data Product",
      title="%s Data Product" % title_prefix,
      individual_variation_base_category_list=["resolution"],
      quantity_unit="unit/piece"
    )
    self.addCleanup(self._removeDocument, resource)
    resource.validate()
    resource_resolution = resource.newContent(
      portal_type="Product Individual Variation",
      title="20S",
    )

    specialise_data_transformation = portal.data_transformation_module.newContent(
      portal_type="Data Transformation",
      title="%s Specialise Data Transformation" % title_prefix,
      resource=resource.getRelativeUrl(),
    )
    self.addCleanup(self._removeDocument, specialise_data_transformation)
    specialise_data_transformation.validate()

    specialise_data_supply = portal.data_supply_module.newContent(
      portal_type="Data Supply",
      title="%s Specialise Data Supply" % title_prefix,
    )
    self.addCleanup(self._removeDocument, specialise_data_supply)
    specialise_data_supply.validate()

    initial_data_analysis = portal.data_analysis_module.newContent(
      portal_type="Data Analysis",
      title="%s Import Raw Data" % title_prefix,
      reference="wendelin.test.16.initial.data.analysis",
      resource=resource.getRelativeUrl(),
      source=test_function_to_organisation['source'].getRelativeUrl(),
      destination=test_function_to_organisation['destination'].getRelativeUrl(),
      specialise_value_list=[
        specialise_data_supply.getRelativeUrl(),
        specialise_data_transformation.getRelativeUrl()
      ],
    )
    self.addCleanup(self._removeDocument, initial_data_analysis)

    initial_data_analysis.start()
    initial_data_analysis.newContent(
      portal_type="Data Analysis Line",
      title="Raw Array",
      reference="out_array",
      resource=resource.getRelativeUrl(),
      quantity=1,
      quantity_unit="unit/piece",
      variation_category_list=[
        "resolution/%s" % resource_resolution.getRelativeUrl(),
        "resource/%s" % resource.getRelativeUrl(),
      ],
      use= "use/big_data/ingestion/stream",
    )
    initial_data_analysis.newContent(
      portal_type="Data Analysis Line",
      title="Convert A to B",
      reference="data_operation",
      resource=data_operation.getRelativeUrl(),
      quantity=1,
      quantity_unit="unit/piece",
    )

    data_transformation = portal.data_transformation_module.newContent(
      portal_type="Data Transformation",
      title="%s Data Transformation" % title_prefix,
      resource=resource.getRelativeUrl(),
    )
    self.addCleanup(self._removeDocument, data_transformation)
    data_transformation.validate()
    data_transformation.newContent(
      portal_type="Data Transformation Operation Line",
      title="Convert A to B",
      reference="data_operation",
      resource=data_operation.getRelativeUrl(),
      quantity=1,
      quantity_unit="unit/piece",
    )

    def getDataAnalysisByTitle(title):
      return portal.portal_catalog.getResultValue(
        portal_type="Data Analysis",
        title=title
      )

    data_analysis_title_list = [specialise_data_transformation.getTitle(), data_transformation.getTitle()]
    for data_analysis_title in data_analysis_title_list:
      self.assertEqual(getDataAnalysisByTitle(data_analysis_title), None)

    self.tic()

    self.portal.portal_alarms.wendelin_handle_analysis.activeSense()
    self.tic()

    for data_analysis_title in data_analysis_title_list:
      data_analysis = getDataAnalysisByTitle(data_analysis_title)
      self.assertNotEqual(data_analysis, None)
      self.addCleanup(self._removeDocument, data_analysis)

  def test_17_DataMapping(self):
    """
    """
    portal = self.portal
    data_mapping = portal.data_mapping_module.newContent(portal_type='Data Mapping')
    self.assertEqual(0, data_mapping.getSize())
    data_list = [
      ('/usr/bin/2to3-2.7', '3ea002bead53f6bdf7', 'fade8568285eb14146a7244', 'f631570af55ee08ecef78f3'),
      ('/usr/bin/R', 'b4c48d52345ae2eb7ca0455db', '59441ddbc00b6521da571', 'a92be1a7acc03f3846'),
      ('/usr/bin/Rscript', 'e97842e556f90be5f7e5', '806725443a01bcae802','1829d887e0c3380ec8f463527'),
      ('/usr/bin/[', '5c348873d0e0abe26d56cc752f0', 'ebb7ae1a78018b62224','9162fdf5b9598c9e9d'),
      ('/usr/bin/aa-enabled', 'c2336b14b7e9d1407d9', 'c8c7af8e6d14a4d1061', '09726542c6c4ca907417c676b4'),
      ('/usr/bin/aa-exec', '7f66cd90da4b27703de299', 'b4bfe90f53a690deb2687342', 'ad36c9002fa84d4e86'),
      ('/usr/bin/aclocal-1.16', '6ba134fb4f97d79a5', '64e518309fc9544b01c164c2e48', 'cc4595fba3251aaa9b48'),
      ('/usr/bin/activate-global-python-argcomplete3', '4007899eba237603a', '8a2584480e9094f9e4761f7', '893ebeeca071795ecd457ed2'),
      ('/usr/bin/addpart', '078a10c409b8b21c3b5137d', '481766f1aa1d393e4a3a', '668374ce14a57b2dd14bb'),
      ('/usr/bin/ansible', 'cb8a161dabae51cf2616c4a85', '31173931d09486697c05', '00ee4c55e8b46f69a54'),
      ('/usr/bin/ansible-connection', 'ffbef34c8d2ae633031f4e8', '61cf10e6b6e4ff33c7ded21244', 'c670ce6af9b645c'),
      ('/usr/bin/ansible-test', '40f528bebb16199d2b11a43b', 'ea6d8680d833fb36e9548a', 'a2c1b309b22cd4285a'),
      ('/usr/bin/appres', '7ccb78e306838a87b68d2c', '7d089e41ee491fc64b2b', 'c3e24ec3fee558e9f06bd0'),
      ('/usr/bin/apt', '3ca60d2b26761b7a50d812', '8b624ea3f31040bd838dfc', '36b5070dd02c87b47512'),
      ('/usr/bin/apt-cache', 'f0e82d30aa1d8a80e', '7da7f514d8056033c4844a6f0', 'be07d8cb7140399252c51c'),
      ('/usr/bin/apt-cdrom', '073483cad694b013a1', 'fb7b20b9450ab7abb4bcc', '2ad240a6670f486e2e1da9daa'),
      ('/usr/bin/apt-config', '32856a9a4e703346d6b8', '407560704903fb078e45dac', 'ee559cd54c2a34f3ad3d4')
    ]
    data_mapped_list = []

    # each different object return a different value
    for data in data_list:
      data_mapped_list.append(data_mapping.addObject(data))
    self.assertEqual(len(data_mapped_list), len(data_list))
    self.assertEqual(len(data_list), data_mapping.getSize())

    # ensure add again same data return always samething
    tmp_list = []
    for data in data_list:
      tmp_list.append(data_mapping.addObject(data))
    self.assertEqual(tmp_list, data_mapped_list)
    # size still same
    self.assertEqual(len(data_list), data_mapping.getSize())

   # ensure we can get original value
    for index in range(len(data_mapped_list)):
      self.assertEqual(data_mapping.getObjectFromValue(data_mapped_list[index]), data_list[index])

  # ensure we can get mapped value
    for index in range(len(data_mapped_list)):
      self.assertEqual(data_mapping.getValueFromObject(data_list[index]), data_mapped_list[index])

    # another data list, /usr/bin/2to3-2.7, /usr/bin/appres, /usr/bin/aclocal-1.16 's value are different compare to previous data
    # so 3 values are different
    another_data_list = [
      ('/usr/bin/2to3-2.7', 'ModifiedValue', 'fade8568285eb14146a7244', 'f631570af55ee08ecef78f3'),
      ('/usr/bin/R', 'b4c48d52345ae2eb7ca0455db', '59441ddbc00b6521da571', 'a92be1a7acc03f3846'),
      ('/usr/bin/Rscript', 'e97842e556f90be5f7e5', '806725443a01bcae802','1829d887e0c3380ec8f463527'),
      ('/usr/bin/[', '5c348873d0e0abe26d56cc752f0', 'ebb7ae1a78018b62224','9162fdf5b9598c9e9d'),
      ('/usr/bin/aa-enabled', 'c2336b14b7e9d1407d9', 'c8c7af8e6d14a4d1061', '09726542c6c4ca907417c676b4'),
      ('/usr/bin/aa-exec', '7f66cd90da4b27703de299', 'b4bfe90f53a690deb2687342', 'ad36c9002fa84d4e86'),
      ('/usr/bin/aclocal-1.16', '6ba134fb4f97d79a5', 'ModifiedValue', 'cc4595fba3251aaa9b48'),
      ('/usr/bin/activate-global-python-argcomplete3', '4007899eba237603a', '8a2584480e9094f9e4761f7', '893ebeeca071795ecd457ed2'),
      ('/usr/bin/addpart', '078a10c409b8b21c3b5137d', '481766f1aa1d393e4a3a', '668374ce14a57b2dd14bb'),
      ('/usr/bin/ansible', 'cb8a161dabae51cf2616c4a85', '31173931d09486697c05', '00ee4c55e8b46f69a54'),
      ('/usr/bin/ansible-connection', 'ffbef34c8d2ae633031f4e8', '61cf10e6b6e4ff33c7ded21244', 'c670ce6af9b645c'),
      ('/usr/bin/ansible-test', '40f528bebb16199d2b11a43b', 'ea6d8680d833fb36e9548a', 'a2c1b309b22cd4285a'),
      ('/usr/bin/appres', '7ccb78e306838a87b68d2c', 'ModifiedValue', 'c3e24ec3fee558e9f06bd0'),
      ('/usr/bin/apt', '3ca60d2b26761b7a50d812', '8b624ea3f31040bd838dfc', '36b5070dd02c87b47512'),
      ('/usr/bin/apt-cache', 'f0e82d30aa1d8a80e', '7da7f514d8056033c4844a6f0', 'be07d8cb7140399252c51c'),
      ('/usr/bin/apt-cdrom', '073483cad694b013a1', 'fb7b20b9450ab7abb4bcc', '2ad240a6670f486e2e1da9daa'),
      ('/usr/bin/apt-config', '32856a9a4e703346d6b8', '407560704903fb078e45dac', 'ee559cd54c2a34f3ad3d4')
    ]

    another_data_mapped_list = []

    for data in another_data_list:
      another_data_mapped_list.append(data_mapping.addObject(data))
    self.assertEqual(len(another_data_mapped_list), len(data_list))

    array = np.array(data_mapped_list)
    another_array = np.array(another_data_mapped_list)
    # simply call setdiff1d to get the different between two datas
    diff_array = np.setdiff1d(another_array, array)
    self.assertEqual(diff_array.size, 3)
    diff_object_list = []
    for value in diff_array:
      diff_object_list.append(data_mapping.getObjectFromValue(value))
    self.assertEqual(diff_object_list, [('/usr/bin/2to3-2.7', 'ModifiedValue', 'fade8568285eb14146a7244', 'f631570af55ee08ecef78f3'),
                                        ('/usr/bin/aclocal-1.16', '6ba134fb4f97d79a5', 'ModifiedValue', 'cc4595fba3251aaa9b48'),
                                        ('/usr/bin/appres', '7ccb78e306838a87b68d2c', 'ModifiedValue', 'c3e24ec3fee558e9f06bd0')])
    # same data value as "another_data_list" but in other format
    other_format_data_list = [
      ['/usr/bin/2to3-2.7', 'ModifiedValue', 'fade8568285eb14146a7244', 'f631570af55ee08ecef78f3'],
      ['/usr/bin/R', 'b4c48d52345ae2eb7ca0455db', '59441ddbc00b6521da571', 'a92be1a7acc03f3846'],
      ['/usr/bin/Rscript', 'e97842e556f90be5f7e5', '806725443a01bcae802','1829d887e0c3380ec8f463527']
    ]
    other_format_data_mapped_list = []
    original_size = data_mapping.getSize()
    for data in other_format_data_list:
      other_format_data_mapped_list.append(data_mapping.addObject(data))
    self.assertEqual(original_size + 3, data_mapping.getSize())
    other_format_array = np.array(other_format_data_mapped_list)
    # ensure "even data values are same but format is different" is considered different
    diff_array = np.setdiff1d(other_format_array, another_array)
    self.assertEqual(diff_array.size, 3)
    diff_object_list = []
    for value in diff_array:
      diff_object_list.append(data_mapping.getObjectFromValue(value))
    self.assertEqual(diff_object_list, [['/usr/bin/2to3-2.7', 'ModifiedValue', 'fade8568285eb14146a7244', 'f631570af55ee08ecef78f3'],
                                        ['/usr/bin/R', 'b4c48d52345ae2eb7ca0455db', '59441ddbc00b6521da571', 'a92be1a7acc03f3846'],
                                        ['/usr/bin/Rscript', 'e97842e556f90be5f7e5', '806725443a01bcae802','1829d887e0c3380ec8f463527']])


  def test_18_wendelinTextToNumpySecurity(self):
    """
      Test that we do not load pickles when converting encoded wendelin data to numpy.
    """
    portal = self.portal
    ndarray = np.array([[0, 1], [2, object()]])
    wendelin_text = base64.b64encode(portal.Base_numpyToWendelinData(ndarray))
    self.assertRaises(ValueError,
                      portal.Base_wendelinTextToNumpy,
                      wendelin_text)
