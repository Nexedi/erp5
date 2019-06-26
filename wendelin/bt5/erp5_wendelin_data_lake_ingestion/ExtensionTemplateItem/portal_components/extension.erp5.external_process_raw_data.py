import os
import csv
import mne
import json
import numpy as np
from DateTime import DateTime
from mne.report import Report
from Products.ERP5Type.Log import log
from lxml.html import parse

CHUNK_SIZE = 200000
CHUNK_SIZE_TXT = 50000
CHUNK_SIZE_CSV = 25
BIG_FILE = 5000000000 #5GB

def saveRawFile(data_stream, file_name):
  data_stream_chunk = None
  n_chunk = 0
  chunk_size = CHUNK_SIZE
  while True:
    start_offset = n_chunk*chunk_size
    end_offset = n_chunk*chunk_size+chunk_size
    try:
      data_stream_chunk = ''.join(data_stream.readChunkList(start_offset, end_offset))
    except:
      raise StandardError("Empty Data Stream")
    if data_stream_chunk == "": break
    with open(file_name, 'a') as fif_file:
      fif_file.write(data_stream_chunk)
    n_chunk += 1

def getJSONfromTextFile(file_name):
  try:
    data = {}
    chunk_size = CHUNK_SIZE_TXT
    with open(file_name, 'r') as text_file:
      first_chunk = text_file.read(chunk_size)
    data["File content sample: "] = first_chunk
    json_data = json.dumps(data)
    return json_data
  except Exception as e:
    log("Error while getting JSON from text file: " + str(e))
    return ""

def getMNEReportJSON(file_name, raw):
  try:
    pattern = file_name + "_raw.fif"
    report_file = file_name + 'report.html'
    os.rename(file_name, pattern)
    report = Report(verbose=True)
    report.parse_folder(data_path="./", pattern=[pattern])
    report.save(report_file, overwrite=True, open_browser=False)
    data = {}
    doc = parse(report_file)
    results = doc.xpath("//table[@class = 'table table-hover']")
    rows = iter(results[0])
    for row in rows:
      data[row[0].text] = row[1].text
    json_data = json.dumps(data)
    return json_data
  except Exception as e:
    log("Error while getting JSON Report: " + str(e))
    return ""
  finally:
    if os.path.exists(pattern):
      os.rename(pattern, file_name)
    if os.path.exists(report_file):
      os.remove(report_file)

def getRawData(file_name):
  raw = None
  try:
    raw = mne.io.read_raw_fif(file_name, preload=False, verbose=None)
  except:
    pass
  if raw is None:
    try:
      raw = mne.io.read_raw_edf(file_name, preload=False, verbose=None)
    except:
      pass
  if raw is None: raise StandardError("the file does not contain raw data.")
  return raw

def processFifData(file_name, data_array, data_descriptor):
  raw = getRawData(file_name)

  try:
    json_report = getMNEReportJSON(file_name, raw)
    data_descriptor.setTextContent(json_report)
  except Exception as e:
    log("Error handling Data Descriptor content: " + str(e))

  picks = mne.pick_types(raw.info)
  if len(picks) == 0: raise StandardError("The raw data does not contain any element")
  data, times = raw[picks[:1]] # get data from first pick to get shape
  dtype = data.dtype

  data_array.initArray(data.shape, dtype)
  zarray = data_array.getArray()
  zarray[0] = data[0]
  data_array.setArray(zarray)

  for pick in xrange(1, len(picks)):
    data, times = raw[pick]
    zarray = data_array.getArray()
    zarray.append(data)
    data_array.setArray(zarray)

def processTextData(file_name, data_array, data_descriptor):
  try:
    json_report = getJSONfromTextFile(file_name)
    data_descriptor.setTextContent(json_report)
  except Exception as e:
    log("Error handling Data Descriptor content: " + str(e))

def processCsvData(file_name, data_array, data_descriptor, delimiter=","):
  def gen_csv_chunks(reader, chunksize=CHUNK_SIZE_CSV):
    chunk = []
    for index, line in enumerate(reader):
      if (index % chunksize == 0 and index > 0):
        yield chunk
        del chunk[:]
      chunk.append(line)
    yield chunk

  def appendArray(array, data_array, columns, initialize=False):
    def getFloat(s):
      try:
        float(s)
        return float(s)
      except:
        return float(0)
    init = 0
    if initialize:
      data_array.initArray((1, columns), np.dtype('float64'))
      zarray = data_array.getArray()
      zarray[0] = [getFloat(x) for x in array[0]]
      data_array.setArray(zarray)
      init = 1
    for i in xrange(init, len(array)):
      if len(array[i]) == columns:
        zarray = data_array.getArray()
        zarray.append([[getFloat(x) for x in array[i]]])
        data_array.setArray(zarray)

  try:
    with open(file_name, 'r') as csv_file:
      reader = csv.reader(csv_file, delimiter=delimiter)
      csv_file.seek(0)
      for i, chunk in enumerate(gen_csv_chunks(reader)):
        if i==0:
          try:
            initialize = True
            columns = len(chunk[0])
            data = {}
            data["csv"] = chunk
            json_data = json.dumps(data)
          except Exception as e:
            log("Error while getting JSON from csv file: " + str(e))
            return ""
        # super inefficient: takes minutes for a csv file of 5MB (57860 rows)
        appendArray(chunk, data_array, columns, initialize)
        # so returning after first chunk
        data_descriptor.setTextContent(json_data)
        return
        initialize = False
      data_descriptor.setTextContent(json_data)
  except Exception as e:
    log("Error handling csv Data Descriptor content: " + str(e))

def processTsvData(file_name, data_array, data_descriptor):
  processCsvData(file_name, data_array, data_descriptor, delimiter="\t")

def processNiiData(file_name, data_array, data_descriptor, gz=False):
  old_file = file_name
  file_name = file_name + ".nii.gz" if gz else file_name + ".nii"
  os.rename(old_file, file_name)
  try:
    import nibabel as nib
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
    data_descriptor.setTextContent(json_data)
  except Exception as e:
    log("Error handling Data Descriptor nii content: " + str(e))
    raise e
  finally:
    os.rename(file_name, old_file)

def processGZData(file_name, data_array, data_descriptor):
  try:
    processNiiData(file_name, data_array, data_descriptor, gz=True)
  except:
    raise KeyError("gz")

def processRawData(data_stream, data_array, data_descriptor, reference_extension):
  content = {"File content":"empty"}
  if data_stream.getSize() == 0:
    data_descriptor.setTextContent(json.dumps(content))
    return "Empty Data Stream"
  if data_stream.getSize() > BIG_FILE:
    log("Ingested file bigger than 5GB, get metadata process skiped")
    return "File bigger than 5GB"

  file_name = "temporal_file_%s" % DateTime().strftime('%Y%m%d-%H%M%S')
  try:
    saveRawFile(data_stream, file_name)
  except Exception as e:
    if os.path.exists(file_name):
      os.remove(file_name)
    return "Error while processing raw data - saving file: " + str(e)

  options = {"fif" : processFifData,
             "nii" : processNiiData,
             "mgz" : processNiiData,
             "txt" : processTextData,
             "csv" : processCsvData,
             "tsv" : processTsvData,
             "gz"  : processGZData,
             "default" : processTextData,
            }
  try:
    if reference_extension in options:
      options[reference_extension](file_name, data_array, data_descriptor)
    else:
      options["default"](file_name, data_array, data_descriptor)
  except KeyError, e:
    return "Proccessing for data in this %s not implemented yet." % reference_extension
  except Exception as e:
    return "Error while processing raw data: " + str(e)
  finally:
    if os.path.exists(file_name):
      os.remove(file_name)


  return "Raw data processed."