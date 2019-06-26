from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
import string
import random
import time
import json
import csv
import os
from datetime import datetime, timedelta
import numpy as np
import math
import base64
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery
from Products.ERP5Type.Log import log
import hashlib

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
  USER = 'zope'
  PASS = 'roque5'
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
    self.context = self.portal.UnitTest_getContext()
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

  def ingestRequest(self, requestMethod, authentication , reference, eof, data_chunk, ingestion):
    encoded_data_chunk = base64.b64encode(data_chunk)
    request = self.portal.REQUEST
    request.method = requestMethod
    request.auth = authentication
    request.set('reference', reference + eof + self.SIZE_HASH)
    request.set('data_chunk', encoded_data_chunk)
    ingestion.ingest()
    self.tic()
    return

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

  def getDataAnalysis(self, reference):
    data_analysis = self.portal.portal_catalog.getResultValue(
                    portal_type = 'Data Analysis',
                    reference = reference)
    return data_analysis

  def getDataArray(self, reference):
    data_array = self.portal.portal_catalog.getResultValue(
                    portal_type = 'Data Array',
                    reference = reference)
    return data_array

  def getDataDescriptor(self, reference):
    data_ingestion = None
    query = ComplexQuery(Query(simulation_state='stopped'),
                     Query(simulation_state='delivered'),
                     logical_operator="OR")
    ing_dict = {
      "query": query,
      "portal_type": "Data Ingestion",
      "reference": reference}
    ingestions = self.portal.portal_catalog(**ing_dict)
    if len(ingestions) == 1:
      data_ingestion = ingestions[0]
    if data_ingestion == None: return None
    url = 'data_descriptor_module/' + data_ingestion.getId()
    data_descriptor = self.context.restrictedTraverse(url)
    return data_descriptor

  def manuallyStopIngestionWorkaround(self, reference, now_time):
    try:
      data_ingestion = self.portal.portal_catalog.getResultValue(
                      portal_type = 'Data Ingestion',
                      reference = reference)
      if data_ingestion.getSimulationState() == "started":
        data_ingestion.stop()
      self.tic()
    except:
      raise StandardError("Could not find ingestion with reference %s" % reference)

  def simulateIngestionAlarm(self, reference, now):
    self.portal.ERP5Site_stopIngestionList()
    self.tic()

    self.portal.ERP5Site_createDataAnalysisList()
    time.sleep(5)
    self.tic()

    self.portal.ERP5Site_executeDataAnalysisList()
    time.sleep(5)
    self.tic()

  def ingest(self, data_chunk, reference, extension):
    ingestion_policy = self.getIngestionPolicy(reference, self.INGESTION_SCRIPT)
    ingestion_reference = self.getIngestionReference(reference, extension)

    now = datetime.now()
    self.ingestRequest('POST', (self.USER, self.PASS), ingestion_reference, self.SINGLE_INGESTION_END, data_chunk, ingestion_policy)
    ingestion_id, ingestion_reference = self.sanitizeReference(ingestion_reference)

    self.simulateIngestionAlarm(ingestion_reference, now)
    return ingestion_reference

  def checkDataObjects(self, ingestion_reference, data_chunk, array, json_data):
    self.checkOperation(None, ingestion_reference, data_chunk, array, json_data)
    return

  def checkOperation(self, ingestion_reference, operation_reference, data_chunk, array, json_data):
    if ingestion_reference != None:
      data_ingestion = self.getDataIngestion(ingestion_reference)
      self.assertEqual(data_ingestion, None)

      data_analysis = self.getDataAnalysis(operation_reference)
      self.assertNotEqual(data_analysis, None)

      data_analysis = self.getDataAnalysis(ingestion_reference)
      self.assertEqual(data_analysis, None)

      data_stream = self.getDataStream(ingestion_reference)
      self.assertEqual(data_stream, None)

      data_array = self.getDataArray(ingestion_reference)
      self.assertEqual(data_array, None)

      data_descriptor = self.getDataDescriptor(ingestion_reference)
      self.assertEqual(data_descriptor, None)

    data_ingestion = self.getDataIngestion(operation_reference)
    self.assertEqual(data_ingestion.getSimulationState(), "delivered")

    size, hash_value = self.context.generateSizeHash(data_chunk)
    data_stream = self.getDataStream(operation_reference)
    self.assertEqual(len(data_chunk), len(data_stream.getData()))
    self.assertEqual(size, data_stream.getSize())
    self.assertEqual(hash_value, data_stream.getVersion())
    self.assertEqual(data_chunk, data_stream.getData())

    data_array = self.getDataArray(operation_reference)
    if array is None:
      self.assertEqual(array, data_array.getArray())
    else:
      np.testing.assert_allclose(array, data_array.getArray()[:])
      self.assertTrue(np.allclose(array, data_array.getArray()[:]))

    if ingestion_reference == None:
      data_descriptor = self.getDataDescriptor(operation_reference)
      self.assertEqual(json_data, data_descriptor.getTextContent())

  def perform_csv_test(self, extension, delimiter):
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
    data = {}
    data["csv"] = chunk
    json_data = json.dumps(data)
    ingestion_reference = self.ingest(data_chunk, reference, extension)

    self.checkDataObjects(ingestion_reference, data_chunk, array[:self.CHUNK_SIZE_CSV], json_data)
    if os.path.exists(file_name):
      os.remove(file_name)

  def perform_nii_test(self, gz):
    import nibabel as nib
    import numpy as np
    reference = self.getRandomReference()
    url = 'data_stream_module/mne_sample_for_test_nii'
    if gz: url += "_gz"
    sample_data_stream = self.context.restrictedTraverse(url)
    data_chunk = sample_data_stream.getData()
    ingestion_reference = self.ingest(data_chunk, reference, self.GZ if gz else self.NII)

    file_name = "file_name.nii"
    if gz: file_name += ".gz"
    with open(file_name, 'w') as nii_file:
      nii_file.write(data_chunk)
    img = nib.load(file_name)
    data = {}
    for key in img.header:
      try:
        if type(img.header[key]) is np.ndarray:
          content = img.header[key].tolist()
          try:
            if np.isnan(img.header[key]): content = "nan"
          except:
            pass
        else:
          content = img.header[key]
        if content == 0: content = "0"
        json.dumps(content)
        if content != "":
          data[key] = content
      except Exception as e:
        pass # ignore non serializable info
    json_data = json.dumps(data)
    if os.path.exists(file_name):
      os.remove(file_name)

    self.checkDataObjects(ingestion_reference, data_chunk, None, json_data)

  def test_full_data_ingestion(self):
    reference = self.getRandomReference()
    data_chunk, nparray, json_data = self.generateRawDataBytesAndArray()
    ingestion_reference = self.ingest(data_chunk, reference, self.FIF)

    self.checkDataObjects(ingestion_reference, data_chunk, nparray, json_data)

  def test_text_data_ingestion(self):
    reference = self.getRandomReference()
    data_chunk = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(self.CHUNK_SIZE_TXT + 1000)])
    ingestion_reference = self.ingest(data_chunk, reference, self.TXT)
    json_data = json.dumps({"File content sample: ": data_chunk[:self.CHUNK_SIZE_TXT]})

    self.checkDataObjects(ingestion_reference, data_chunk, None, json_data)

  def test_tsv_data_ingestion(self):
    delimiter = "\t"
    extension = self.TSV
    self.perform_csv_test(extension, delimiter)

  def test_csv_data_ingestion(self):
    delimiter = ","
    extension = self.CSV
    self.perform_csv_test(extension, delimiter)

  def test_default_text_data_ingestion(self):
    reference = self.getRandomReference()
    data_chunk = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(self.CHUNK_SIZE_TXT + 1000)])
    ingestion_reference = self.ingest(data_chunk, reference, self.RANDOM)
    json_data = json.dumps({"File content sample: ": data_chunk[:self.CHUNK_SIZE_TXT]})

    self.checkDataObjects(ingestion_reference, data_chunk, None, json_data)

  def test_nii_data_ingestion(self):
    self.perform_nii_test(gz=False)

  def test_nii_gz_data_ingestion(self):
    self.perform_nii_test(gz=True)

  def test_data_ingestion_split_file(self):
    reference = self.getRandomReference()
    ingestion_policy = self.getIngestionPolicy(reference, self.INGESTION_SCRIPT)
    data_chunk_1 = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(250)])
    data_chunk_2 = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(250)])
    data_chunk_3 = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(250)])
    data_chunk_4 = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(250)])
    data_chunk = data_chunk_1 + data_chunk_2 + data_chunk_3 + data_chunk_4
    ingestion_reference = self.getIngestionReference(reference, self.FIF)
    self.ingestRequest('POST', (self.USER, self.PASS), ingestion_reference, self.PART_1, data_chunk_1, ingestion_policy)
    time.sleep(1)
    self.ingestRequest('POST', (self.USER, self.PASS), ingestion_reference, self.PART_2, data_chunk_2, ingestion_policy)
    time.sleep(1)
    self.ingestRequest('POST', (self.USER, self.PASS), ingestion_reference, self.PART_3, data_chunk_3, ingestion_policy)
    time.sleep(1)
    self.ingestRequest('POST', (self.USER, self.PASS), ingestion_reference, self.EOF, data_chunk_4, ingestion_policy)
    self.portal.ERP5Site_stopIngestionList()
    self.tic()
    ingestion_id, ingestion_reference = self.sanitizeReference(ingestion_reference)
    data_stream = self.getDataStream(ingestion_reference)
    self.assertEqual(len(data_chunk), len(data_stream.getData()))
    self.assertEqual(data_chunk, data_stream.getData())

  def test_deletion(self):
    reference = self.getRandomReference()
    data_chunk = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(self.CHUNK_SIZE_TXT + 1000)])
    ingestion_reference = self.ingest(data_chunk, reference, self.TXT)
    json_data = json.dumps({"File content sample: ": data_chunk[:self.CHUNK_SIZE_TXT]})
    self.checkDataObjects(ingestion_reference, data_chunk, None, json_data)
    self.portal.ERP5Site_invalidateIngestionObjects(ingestion_reference)
    self.tic()
    invalid_reference = ingestion_reference + self.INVALID
    self.checkOperation(ingestion_reference, invalid_reference, data_chunk, None, json_data)

  def test_rename(self):
    reference = self.getRandomReference()
    data_chunk = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(self.CHUNK_SIZE_TXT + 1000)])
    ingestion_reference = self.ingest(data_chunk, reference, self.TXT)
    json_data = json.dumps({"File content sample: ": data_chunk[:self.CHUNK_SIZE_TXT]})
    self.checkDataObjects(ingestion_reference, data_chunk, None, json_data)
    new_ingestion_reference = ingestion_reference + self.NEW
    self.portal.ERP5Site_renameIngestion(ingestion_reference, new_ingestion_reference)
    self.tic()
    self.checkOperation(ingestion_reference, new_ingestion_reference, data_chunk, None, json_data)

  def test_reingestion(self):
    reference = self.getRandomReference()
    data_chunk = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(self.CHUNK_SIZE_TXT + 1000)])
    ingestion_reference = self.ingest(data_chunk, reference, self.TXT)
    json_data = json.dumps({"File content sample: ": data_chunk[:self.CHUNK_SIZE_TXT]})
    self.checkDataObjects(ingestion_reference, data_chunk, None, json_data)
    new_data_chunk = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(self.CHUNK_SIZE_TXT + 1000)])
    new_json_data = json.dumps({"File content sample: ": new_data_chunk[:self.CHUNK_SIZE_TXT]})
    ingestion_reference = self.ingest(new_data_chunk, reference, self.TXT)
    self.checkDataObjects(ingestion_reference, new_data_chunk, None, new_json_data)

  def test_reference_exists(self):
    reference = self.getRandomReference()
    data_chunk = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(self.CHUNK_SIZE_TXT + 1000)])
    ingestion_reference = self.ingest(data_chunk, reference, self.TXT)
    json_data = json.dumps({"File content sample: ": data_chunk[:self.CHUNK_SIZE_TXT]})
    self.checkDataObjects(ingestion_reference, data_chunk, None, json_data)
    size, hash_value = self.context.generateSizeHash(data_chunk)
    full_reference = self.getFullReference(ingestion_reference, size, hash_value)
    exists = self.portal.ingestionReferenceExists(full_reference)
    self.assertEqual(exists, self.TRUE)

  def test_descriptor_html_content_script(self):
    reference = self.getRandomReference()
    data_chunk = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(self.CHUNK_SIZE_TXT + 1000)])
    ingestion_reference = self.ingest(data_chunk, reference, self.TXT)
    json_data = json.dumps({"File content sample: ": data_chunk[:self.CHUNK_SIZE_TXT]})
    self.checkDataObjects(ingestion_reference, data_chunk, None, json_data)
    script_content = self.portal.getDescriptorHTMLContent(ingestion_reference)
    self.assertEqual(script_content, json_data)

'''
  def test_data_stream_invalidation(self):
    reference = self.getRandomReference()
    data_chunk = ''.join([random.choice(string.ascii_letters + string.digits) for _ in xrange(self.CHUNK_SIZE_TXT + 1000)])
    ingestion_reference = self.ingest(data_chunk, reference, self.TXT)
    json_data = json.dumps({"File content sample: ": data_chunk[:self.CHUNK_SIZE_TXT]})
    self.checkDataObjects(ingestion_reference, data_chunk, None, json_data)
    #self.portal.data_stream_module.invalidateObject(data_stream.getId())
    self.tic()
    invalid_reference = ingestion_reference + self.INVALID
    self.checkOperation(ingestion_reference, invalid_reference, data_chunk, None, json_data)
'''

  # TODOs

  #def test_object_invalidation(self):

  #def test_deletion_rename_and_reingestion_on_split_ingestion(self):

  #def test_descriptor_html_content_script_on_middle_of_ingestion(self):

  #def test_usual_features_on_middle_of_ingestion(self):



