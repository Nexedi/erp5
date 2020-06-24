import hashlib
import base64
from Products.ZSQLCatalog.SQLCatalog import Query

CHUNK_SIZE = 200000

def getHash(data_stream):
  hash_md5 = hashlib.md5()
  data_stream_chunk = None
  n_chunk = 0
  chunk_size = CHUNK_SIZE
  while True:
    start_offset = n_chunk*chunk_size
    end_offset = n_chunk*chunk_size+chunk_size
    try:
      data_stream_chunk = ''.join(data_stream.readChunkList(start_offset, end_offset))
    except Exception:
      # data stream is empty
      data_stream_chunk = ""
    hash_md5.update(data_stream_chunk)
    if data_stream_chunk == "": break
    n_chunk += 1
  return hash_md5.hexdigest()

decoded = base64.b64decode(data_chunk)
data_stream.appendData(decoded)
data_stream.setVersion(getHash(data_stream))

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog
reference_end_split = portal.ERP5Site_getIngestionReferenceDictionary()["split_end_suffix"]

#if last chunk of split ingestion -> validate all related data streams and publish the current one:
if data_stream.getId().endswith(reference_end_split):
  query = Query(portal_type="Data Stream", reference=data_stream.getReference(), validation_state="draft")
  split_ingestion_data_stream_list = portal_catalog(query=query, sort_on=(('creation_date', 'ascending'),))
  #full_file_size = 0
  for chunk_data_stream in split_ingestion_data_stream_list:
    #full_file_size += chunk_data_stream.getSize()
    if chunk_data_stream.getValidationState() != "validated":
      chunk_data_stream.validate()
  if data_stream.getValidationState() != "validated":
    data_stream.validate()
    data_stream.publish()
