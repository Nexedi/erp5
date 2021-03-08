from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
import string
import random
import csv
import os
import time
import numpy as np
import base64

class TestDataIngestion(SecurityTestCase):

  REFERENCE_SEPARATOR = "/"
  PART_1 = REFERENCE_SEPARATOR + "001"
  PART_2 = REFERENCE_SEPARATOR + "002"
  PART_3 = REFERENCE_SEPARATOR + "003"
  EOF = REFERENCE_SEPARATOR + "EOF"
  FIF = REFERENCE_SEPARATOR + "fif"
  CSV = REFERENCE_SEPARATOR + "csv"
  SIZE_HASH = REFERENCE_SEPARATOR + "fake-size"+ REFERENCE_SEPARATOR + "fake-hash"
  SINGLE_INGESTION_END = REFERENCE_SEPARATOR
  CHUNK_SIZE_CSV = 25
  REF_PREFIX = "fake-supplier" + REFERENCE_SEPARATOR
  REF_SUPPLIER_PREFIX = "fake-supplier" + REFERENCE_SEPARATOR
  INVALID = "_invalid"
  REF_DATASET = "fake-dataset"

  def getTitle(self):
    return "DataIngestionTest"

  def afterSetUp(self):
    self.assertEqual(self.REFERENCE_SEPARATOR, self.portal.ERP5Site_getIngestionReferenceDictionary()["reference_separator"])
    self.assertEqual(self.INVALID, self.portal.ERP5Site_getIngestionReferenceDictionary()["invalid_suffix"])
    self.assertEqual(self.EOF, self.REFERENCE_SEPARATOR + self.portal.ERP5Site_getIngestionReferenceDictionary()["split_end_suffix"])
    self.assertEqual(self.PART_1, self.REFERENCE_SEPARATOR + self.portal.ERP5Site_getIngestionReferenceDictionary()["split_first_suffix"])

  def getRandomReference(self):
    random_string = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(10)])
    return 'UNIT-TEST-' + random_string

  def getIngestionReference(self, reference, extension, randomize_ingestion_reference=False, data_set_reference=False):
    if not data_set_reference:
      data_set_reference = self.REF_DATASET
    if not randomize_ingestion_reference:
      # return hard coded which results in one Data Set and multiple Data Streams (in context of test)
      return self.REF_PREFIX + data_set_reference + self.REFERENCE_SEPARATOR + reference + extension
    else:
      # create random one
      random_string = self.getRandomReference()
      return "%s/%s/%s/csv//fake-size/fake-hash" %(random_string, random_string, random_string)

  def sanitizeReference(self, reference):
    ingestion_reference = self.REFERENCE_SEPARATOR.join(reference.split(self.REFERENCE_SEPARATOR)[1:])
    data_stream = self.getDataStream(ingestion_reference)
    ingestion_id = data_stream.getId()
    return ingestion_id, ingestion_reference

  def getFullReference(self, ingestion_reference, size, hash_value):
    return self.REF_SUPPLIER_PREFIX + ingestion_reference + self.REFERENCE_SEPARATOR +  self.REFERENCE_SEPARATOR + str("") +  self.REFERENCE_SEPARATOR + ""

  def chunks(self, l, n):
    for i in xrange(0, len(l), n):
      yield l[i:i+n]

  def getDataIngestion(self, reference):
    data_ingestion = self.portal.portal_catalog.getResultValue(
                    portal_type = 'Data Ingestion',
                    reference = reference)
    return data_ingestion

  def getDataStream(self, reference):
    data_stream = self.portal.portal_catalog.getResultValue(
                    portal_type = 'Data Stream',
                    reference = reference)
    return data_stream

  def getDataStreamChunkList(self, reference):
    data_stream_list = self.portal.portal_catalog(
                        portal_type = 'Data Stream',
                        reference = reference,
                        sort_on=[('creation_date', 'ascending')])
    return data_stream_list

  def ingestRequest(self, reference, eof, data_chunk, ingestion_policy):
    encoded_data_chunk = base64.b64encode(data_chunk)
    request = self.portal.REQUEST
    # only POST for Wendelin allowed
    request.environ["REQUEST_METHOD"] = 'POST'
    reference = reference + eof + self.SIZE_HASH
    self.portal.log("Ingest with reference=%s" %reference)
    request.set('reference', reference)
    request.set('data_chunk', encoded_data_chunk)
    ingestion_policy.ingest()
    self.tic()

  def ingest(self, data_chunk, reference, extension, eof, randomize_ingestion_reference=False, data_set_reference=False):
    ingestion_reference = self.getIngestionReference(reference, extension, randomize_ingestion_reference, data_set_reference)
    # use default ebulk policy
    ingestion_policy = self.portal.portal_ingestion_policies.default_ebulk
    self.ingestRequest(ingestion_reference, eof, data_chunk, ingestion_policy)
    _, ingestion_reference = self.sanitizeReference(ingestion_reference)
    return ingestion_reference

  def stepIngest(self, extension, delimiter, randomize_ingestion_reference=False, data_set_reference=False):
    file_name = "file_name.csv"
    reference = self.getRandomReference()
    array = [[random.random() for i in range(self.CHUNK_SIZE_CSV + 10)] for j in range(self.CHUNK_SIZE_CSV + 10)]
    np.savetxt(file_name, array, delimiter=delimiter)
    chunk = []
    with open(file_name, 'r') as csv_file:
      data_chunk = csv_file.read()
      csv_file.seek(0)
      reader = csv.reader(csv_file, delimiter=delimiter)
      for index, line in enumerate(reader):
        if (index < self.CHUNK_SIZE_CSV):
          chunk.append(line)
        else:
          break
    ingestion_reference = self.ingest(data_chunk, reference, extension, self.SINGLE_INGESTION_END,
                                      randomize_ingestion_reference=randomize_ingestion_reference, data_set_reference=data_set_reference)

    if os.path.exists(file_name):
      os.remove(file_name)

    # test properly ingested
    data_ingestion = self.getDataIngestion(ingestion_reference)
    self.assertNotEqual(None, data_ingestion)

    data_ingestion_line = [x for x in data_ingestion.objectValues() \
                            if x.getReference() == 'out_stream'][0]
    data_set = data_ingestion_line.getAggregateValue(portal_type='Data Set')
    data_stream = data_ingestion_line.getAggregateValue(portal_type='Data Stream')
    self.assertNotEqual(None, data_stream)

    data_stream_data = data_stream.getData()
    self.assertEqual(data_chunk, data_stream_data)

    return data_set, [data_stream]

  def test_01_DefaultEbulkIngestion(self):
    """
      Test default ingestion with ebulk too.
    """
    data_set, data_stream_list = self.stepIngest(self.CSV, ",", randomize_ingestion_reference=True)

    # check Data Set and Data Stream is validated
    self.assertEqual('validated', data_set.getValidationState())
    self.assertSameSet(['validated' for x in data_stream_list],
                       [x.getValidationState() for x in data_stream_list])

  def test_02_DefaultSplitIngestion(self):
    """
      Test multiple uploads from ebulk end up in multiple Data Streams
      (in case of large file upload when ebluk by default splits file to 50MBs
      chunks).
    """
    data_chunk_1 = ''.join([random.choice(string.ascii_letters + string.digits) \
                              for _ in xrange(250)])
    data_chunk_2 = ''.join([random.choice(string.ascii_letters + string.digits) \
                              for _ in xrange(250)])
    data_chunk_3 = ''.join([random.choice(string.ascii_letters + string.digits) \
                              for _ in xrange(250)])
    data_chunk_4 = ''.join([random.choice(string.ascii_letters + string.digits) \
                              for _ in xrange(250)])

    reference = self.getRandomReference()

    ingestion_reference = self.ingest(data_chunk_1, reference, self.FIF, self.PART_1)
    time.sleep(1)
    self.tic()

    ingestion_reference = self.ingest(data_chunk_2, reference, self.FIF, self.PART_2)
    time.sleep(1)
    self.tic()

    ingestion_reference = self.ingest(data_chunk_3, reference, self.FIF, self.PART_3)
    time.sleep(1)
    self.tic()

    ingestion_reference = self.ingest(data_chunk_4, reference, self.FIF, self.EOF)
    time.sleep(1)
    self.tic()

    # call explicitly alarm so all 4 Data Streams are validated and published
    self.portal.portal_alarms.wendelin_handle_analysis.Alarm_handleAnalysis()
    self.tic()

    # check resulting Data Streams
    data_stream_list = self.getDataStreamChunkList(ingestion_reference)
    #one data stream per chunk
    self.assertEqual(len(data_stream_list), 4)
    #all data streams are validated
    self.assertSameSet(['validated' for x in data_stream_list],
                       [x.getValidationState() for x in data_stream_list])
    #data streams are linked
    data_stream_1 = data_stream_list[0].getObject()
    data_stream_2 = data_stream_list[1].getObject()
    data_stream_3 = data_stream_list[2].getObject()
    data_stream_4 = data_stream_list[3].getObject()
    # test successor
    self.assertSameSet(data_stream_2.getRecursiveSuccessorValueList(), \
                       [data_stream_3, data_stream_4])
    self.assertSameSet(data_stream_4.getRecursiveSuccessorValueList(), \
                       [])
    # test predecessor
    self.assertSameSet(data_stream_1.getRecursivePredecessorValueList(), \
                       [])
    self.assertSameSet(data_stream_2.getRecursivePredecessorValueList(), \
                       [data_stream_1])
    self.assertSameSet(data_stream_4.getRecursivePredecessorValueList(), \
                       [data_stream_3, data_stream_2, data_stream_1])

  def test_03_DefaultWendelinConfigurationExistency(self):
    """
      Test that nobody accidently removes needed by HowTo's default configurations.
    """
    # test default ebuk ingestion exists
    self.assertNotEqual(None,
           getattr(self.portal.portal_ingestion_policies, "default_ebulk", None))
    self.assertNotEqual(None,
           getattr(self.portal.data_supply_module, "default_ebulk", None))

  def test_04_DatasetAndDatastreamsConsistency(self):
    """
      Test that data set state transition also changes its data streams states
    """
    data_set, data_stream_list = self.stepIngest(self.CSV, ",", randomize_ingestion_reference=True)
    self.tic()

    # check data relation between Data Set and Data Streams work
    self.assertSameSet(data_stream_list, data_set.DataSet_getDataStreamList())

    # check data set and all Data Streams states
    self.assertEqual('validated', data_set.getValidationState())
    self.assertSameSet(['validated' for x in data_stream_list],
                       [x.getValidationState() for x in data_stream_list])

    # publish data set and have all Data Streams publsihed automatically
    data_set.publish()
    self.tic()
    self.assertEqual('published', data_set.getValidationState())
    self.assertSameSet(['published' for x in data_stream_list],
                       [x.getValidationState() for x in data_stream_list])

    # invalidate Data Set should invalidate related Data Streams
    data_set.invalidate()
    self.tic()
    self.assertEqual('invalidated', data_set.getValidationState())
    self.assertSameSet(['invalidated' for x in data_stream_list],
                       [x.getValidationState() for x in data_stream_list])

  def test_05_StateConsistencyAlarm(self):
    """
      Test alarm that checks (and fixes) Data set - Data stream state consistency
    """
    data_set_reference = "consistency-dataset-" + self.getRandomReference()
    data_set, data_stream_list = self.stepIngest(self.CSV, ",",
                                      randomize_ingestion_reference=False, data_set_reference=data_set_reference)
    self.tic()
    first_file_stream = data_stream_list[0]

    # publish Data Set (all Data Streams are published automatically)
    data_set.publish()
    self.tic()

    # ingest new file
    data_set, data_stream_list = self.stepIngest(self.CSV, ",",
                                      randomize_ingestion_reference=False, data_set_reference=data_set_reference)
    self.tic()
    second_file_stream = data_stream_list[0]

    # second ingested file stream is in validated state (inconsistent with whole data set state)
    self.assertEqual(data_set.getValidationState(), 'published')
    self.assertEqual(first_file_stream.getValidationState(), 'published')
    self.assertEqual(second_file_stream.getValidationState(), 'validated')

    # call explicitly alarm to fix the state inconsistency
    self.portal.portal_alarms.wendelin_check_datastream_consistency.Alarm_checkDataStreamStateConsistency()
    self.tic()

    # check states where updated (all published)
    self.assertEqual(data_set.getValidationState(), 'published')
    self.assertEqual(first_file_stream.getValidationState(), 'published')
    self.assertEqual(second_file_stream.getValidationState(), 'published')

  def test_06_IngestSameElementTwice(self):
    """
      Try to ingest same element twice while previous is being processed
    """
    reference = self.getRandomReference()

    self.ingest("some-data", reference, self.CSV, self.SINGLE_INGESTION_END)
    time.sleep(1)
    self.tic()

    #ingest with same reference while previous was not processed should fail
    self.assertRaises(Exception, self.ingest, "some-data", reference, self.CSV, self.SINGLE_INGESTION_END)

  def test_07_IngestionReplacesOld(self):
    """
      Try to ingest same element twice while previous is being processed
    """
    reference = self.getRandomReference()

    self.ingest("some-data", reference, self.CSV, self.SINGLE_INGESTION_END)
    time.sleep(1)
    self.tic()

    # call explicitly alarm to process and validate the ingestion
    self.portal.portal_alarms.wendelin_handle_analysis.Alarm_handleAnalysis()
    self.tic()

    ingestion_reference = self.REF_DATASET + self.REFERENCE_SEPARATOR + reference + self.CSV
    data_ingestion = self.getDataIngestion(ingestion_reference)
    data_stream = self.getDataStream(ingestion_reference)

    self.assertEqual(data_ingestion.getSimulationState(), "stopped")
    self.assertEqual(data_stream.getValidationState(), "validated")

    # the new ingestion should replace the old one
    self.ingest("some-data", reference, self.CSV, self.SINGLE_INGESTION_END)
    time.sleep(1)
    self.tic()

    self.assertEqual(data_stream.getValidationState(), "invalidated")
    self.assertTrue(data_ingestion.getReference().endswith(self.INVALID))

  def test_08_checkAlarms(self):
    """
      Check all data analysis and data transformations are well configured
    """
    # call two times the alarm (1. create analysis 2. run analysis)
    self.portal.portal_alarms.wendelin_handle_analysis.Alarm_handleAnalysis()
    self.tic()
    self.portal.portal_alarms.wendelin_handle_analysis.Alarm_handleAnalysis()
    self.tic()

  def test_10_checkDataSetDataStreamRelation(self):
    """
      Data Set and its Data Streams are related through the corresponding Data Ingestion Lines
    """
    # ingest a couple of files
    reference = self.getRandomReference()
    self.ingest("some-data-1", reference, self.CSV, self.SINGLE_INGESTION_END)
    time.sleep(1)
    self.tic()
    reference += "-2"
    self.ingest("some-data-2", reference, self.CSV, self.SINGLE_INGESTION_END)
    time.sleep(1)
    self.tic()
    # get corresponding Data Streams by searching via Data Ingestion Lines of the Data Set
    data_set = self.portal.data_set_module.get(self.REF_DATASET)
    data_ingestion_line_list = self.portal.portal_catalog(
                    portal_type = 'Data Ingestion Line',
                    aggregate_uid = data_set.getUid())
    data_ingestion_uid_list = [x.getUid() for x in data_ingestion_line_list]
    data_stream_list = self.portal.portal_catalog(
                    portal_type = 'Data Stream',
                    aggregate__related__uid = data_ingestion_uid_list,
                    select_list = ['reference', 'relative_url', 'versioning.size', 'versioning.version'])
    data_stream_list = [x.getObject() for x in data_stream_list]
    # assert that the list from the search is the same as DataSet_getDataStreamList
    self.assertSameSet(data_stream_list, data_set.DataSet_getDataStreamList())

  # XXX: new test which simulates download / upload of Data Set and increase DS version