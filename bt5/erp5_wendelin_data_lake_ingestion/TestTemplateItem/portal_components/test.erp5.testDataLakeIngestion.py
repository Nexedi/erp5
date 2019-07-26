from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
import string
import random
import csv
import os
import time
import numpy as np
import base64
from datetime import datetime

class TestDataIngestion(SecurityTestCase):

  REFERENCE_SEPARATOR = "/"
  PART_1 = REFERENCE_SEPARATOR + "001"
  PART_2 = REFERENCE_SEPARATOR + "002"
  PART_3 = REFERENCE_SEPARATOR + "003"
  EOF = REFERENCE_SEPARATOR + "EOF"
  FIF = REFERENCE_SEPARATOR + "fif"
  TXT = REFERENCE_SEPARATOR + "txt"
  CSV = REFERENCE_SEPARATOR + "csv"
  TSV = REFERENCE_SEPARATOR + "tsv"
  GZ = REFERENCE_SEPARATOR + "gz"
  NII = REFERENCE_SEPARATOR + "nii"
  SIZE_HASH = REFERENCE_SEPARATOR + "fake-size"+ REFERENCE_SEPARATOR + "fake-hash"
  SINGLE_INGESTION_END = REFERENCE_SEPARATOR
  RANDOM = REFERENCE_SEPARATOR + ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(3)])
  CHUNK_SIZE_TXT = 50000
  CHUNK_SIZE_CSV = 25
  REF_PREFIX = "fake-supplier" + REFERENCE_SEPARATOR + "fake-dataset" + REFERENCE_SEPARATOR
  REF_SUPPLIER_PREFIX = "fake-supplier" + REFERENCE_SEPARATOR
  INGESTION_SCRIPT = 'HandleFifEmbulkIngestion'
  INVALID = "_invalid"
  NEW = "_NEW"
  FALSE = "FALSE"
  TRUE = "TRUE"

  def getTitle(self):
    return "DataIngestionTest"

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_web', 'erp5_ingestion_mysql_innodb_catalog', 'erp5_ingestion', 'erp5_dms',
            'erp5_wendelin', 'erp5_callables', 'erp5_core')

  def afterSetUp(self):
    self.context = self.portal #.UnitTest_getContext()
    self.assertEqual(self.REFERENCE_SEPARATOR, self.portal.getIngestionReferenceDictionary()["reference_separator"])
    self.assertEqual(self.INVALID, self.portal.getIngestionReferenceDictionary()["invalid_suffix"])
    self.assertEqual(self.EOF, self.REFERENCE_SEPARATOR + self.portal.getIngestionReferenceDictionary()["split_end_suffix"])
    self.assertEqual(self.SINGLE_INGESTION_END, self.REFERENCE_SEPARATOR)
    self.assertEqual(self.PART_1, self.REFERENCE_SEPARATOR + self.portal.getIngestionReferenceDictionary()["split_first_suffix"])

  def getRandomReference(self):
    random_string = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(10)])
    return 'UNIT-TEST-' + random_string

  def getIngestionReference(self, reference, extension):
    return self.REF_PREFIX + reference + extension

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

  def generateRawDataBytesAndArray(self):
    url = 'data_stream_module/mne_sample_for_test'
    sample_data_stream = self.context.restrictedTraverse(url)
    raw_data, array, json_data = self.context.generateRawData(sample_data_stream)
    return raw_data, array, json_data

  def getIngestionPolicy(self, reference, ingestion_script):
    ingestion_policy = self.portal.portal_catalog.getResultValue(
                    portal_type = 'Ingestion Policy',
                    reference = reference)
    if ingestion_policy != None: return ingestion_policy
    ingestion_policy = self.portal.portal_ingestion_policies.newContent( \
        id = reference,
        portal_type ='Ingestion Policy',
        reference = reference,
        version = '001',
        script_id = ingestion_script)
    ingestion_policy.validate()
    self.tic()
    return ingestion_policy
    
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
    return

  def ingest(self, data_chunk, reference, extension, eof):
    ingestion_reference = self.getIngestionReference(reference, extension)
    
    # use default ebulk policy
    ingestion_policy = self.portal.portal_ingestion_policies.wendelin_embulk
    
    self.ingestRequest(ingestion_reference, eof, data_chunk, ingestion_policy)
    ingestion_id, ingestion_reference = self.sanitizeReference(ingestion_reference)

    return ingestion_reference     

  def stepIngest(self, extension, delimiter):
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

    ingestion_reference = self.ingest(data_chunk, reference, extension, self.SINGLE_INGESTION_END)
    
    if os.path.exists(file_name):
      os.remove(file_name)
    
    # test properly ingested
    data_ingestion = self.getDataIngestion(ingestion_reference)
    self.assertNotEqual(None, data_ingestion)
    
    data_ingestion_line = [x for x in data_ingestion.objectValues() \
                            if x.getReference() == 'out_stream'][0]

    data_stream = data_ingestion_line.getAggregateValue(portal_type='Data Stream')
    self.assertNotEqual(None, data_stream)

    data_stream_data = data_stream.getData()
    self.assertEqual(data_chunk, data_stream_data)
    
  def test_01_DefaultEbulkIngestion(self):
    """
      Test default ingestion with ebulk too.
    """
    delimiter = ","
    extension = self.CSV
    self.stepIngest(extension, delimiter)
    
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
