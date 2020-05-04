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
  REF_PREFIX = "fake-supplier" + REFERENCE_SEPARATOR + "fake-dataset" + REFERENCE_SEPARATOR
  REF_SUPPLIER_PREFIX = "fake-supplier" + REFERENCE_SEPARATOR
  INVALID = "_invalid"

  def getTitle(self):
    return "DataIngestionTest"

  def afterSetUp(self):
    self.assertEqual(self.REFERENCE_SEPARATOR, self.portal.getIngestionReferenceDictionary()["reference_separator"])
    self.assertEqual(self.INVALID, self.portal.getIngestionReferenceDictionary()["invalid_suffix"])
    self.assertEqual(self.EOF, self.REFERENCE_SEPARATOR + self.portal.getIngestionReferenceDictionary()["split_end_suffix"])
    self.assertEqual(self.PART_1, self.REFERENCE_SEPARATOR + self.portal.getIngestionReferenceDictionary()["split_first_suffix"])

  def getRandomReference(self):
    random_string = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(10)])
    return 'UNIT-TEST-' + random_string

  def getIngestionReference(self, reference, extension, randomize_ingestion_reference=False):
    if not randomize_ingestion_reference:
      # return hard coded which results in one Data Set and multiple Data Streams (in context of test)
      return self.REF_PREFIX + reference + extension
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

  def ingest(self, data_chunk, reference, extension, eof, randomize_ingestion_reference=False):
    ingestion_reference = self.getIngestionReference(reference, extension, randomize_ingestion_reference)
    self.portal.log(ingestion_reference)
    
    # use default ebulk policy
    ingestion_policy = self.portal.portal_ingestion_policies.wendelin_embulk
    
    self.ingestRequest(ingestion_reference, eof, data_chunk, ingestion_policy)
    _, ingestion_reference = self.sanitizeReference(ingestion_reference)

    return ingestion_reference     

  def stepIngest(self, extension, delimiter, randomize_ingestion_reference=False):
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

    ingestion_reference = self.ingest(data_chunk, reference, extension, self.SINGLE_INGESTION_END, randomize_ingestion_reference=randomize_ingestion_reference)
    
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

    # check Data Stream and Data Set are validated
    self.assertEqual('validated', data_stream.getValidationState())

    return data_set, [data_stream]

  def test_01_DefaultEbulkIngestion(self):
    """
      Test default ingestion with ebulk too.
    """
    self.stepIngest(self.CSV, ",")
    
  def test_02_DefaultSplitIngestion(self):
    """
      Test multiple uploads from ebulk end up in same Data Stream concatenated 
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
    data_chunk = data_chunk_1 + data_chunk_2 + data_chunk_3 + data_chunk_4
    
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
    
    # call explicitly alarm so all 4 Data Streams can be concatenated to one
    self.portal.portal_alarms.wendelin_data_lake_handle_analysis.Alarm_dataLakeHandleAnalysis()
    self.tic()
    
    # check resulting Data Stream
    data_stream = self.getDataStream(ingestion_reference)
    self.assertEqual(data_chunk, data_stream.getData())

  def test_03_DefaultWendelinConfigurationExistency(self):
    """
      Test that nobody accidently removes needed by HowTo's default configurations.
    """ 
    # test default ebuk ingestion exists
    self.assertNotEqual(None, 
           getattr(self.portal.portal_ingestion_policies, "wendelin_embulk", None))
    self.assertNotEqual(None, 
           getattr(self.portal.data_supply_module, "embulk", None))

  def test_04_DefaultModelSecurityModel(self):
    """
      Test default security model : 'All can download, only contributors can upload.'
    """
    data_set, data_stream_list = self.stepIngest(self.CSV, ",", randomize_ingestion_reference=True)
    self.tic()
    
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

  # XXX: new test which simulates download / upload of Data Set and increase DS version