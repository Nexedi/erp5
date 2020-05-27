from Products.ERP5Type.Log import log
from Products.ZSQLCatalog.SQLCatalog import Query
import hashlib

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

def isFinishedSplitIngestion(reference):
  #check if all chunks of a split file were ingested
  #that is if EOF chunk was ingested
  reference_end_split = portal.ERP5Site_getIngestionReferenceDictionary()["split_end_suffix"]
  eof_ingestion = portal_catalog(portal_type = "Data Ingestion",
                                 simulation_state = "started",
                                 reference = reference,
                                 id = "%"+reference_end_split)
  return len(eof_ingestion) == 1

def isInterruptedAbandonedSplitIngestion(reference):
  from DateTime import DateTime
  day_hours = 1.0/24/60*60*24
  # started split data ingestions for reference
  catalog_kw = {'portal_type': 'Data Ingestion',
                'simulation_state': 'started',
                'reference': reference}
  invalidate = True
  for data_ingestion in portal_catalog(**catalog_kw):
    # check that all related ingestions are old (more than 24 hours)
    if (DateTime() - data_ingestion.getCreationDate()) < day_hours:
      invalidate = False
  return invalidate

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

reference_end_single = portal.ERP5Site_getIngestionReferenceDictionary()["single_end_suffix"]
reference_first_split = portal.ERP5Site_getIngestionReferenceDictionary()["split_first_suffix"]
reference_end_split = portal.ERP5Site_getIngestionReferenceDictionary()["split_end_suffix"]

# stop single started ingestion (not split files)
for data_ingestion in portal_catalog(portal_type = "Data Ingestion",
                                     simulation_state = "started",
                                     id = "%"+reference_end_single):
  if not portal.ERP5Site_checkReferenceInvalidated(data_ingestion):
    related_split_ingestions = portal_catalog(portal_type = "Data Ingestion",
                                              reference = data_ingestion.getReference())
    if len(related_split_ingestions) == 1:
      try:
        data_stream = portal_catalog.getResultValue(
          portal_type = 'Data Stream',
          reference = data_ingestion.getReference())
        if data_stream is not None:
          if data_stream.getVersion() is None:
            hash_value = getHash(data_stream)
            data_stream.setVersion(hash_value)
          if data_stream.getValidationState() != "validated" and data_stream.getValidationState() != "published":
            data_stream.validate()
          if data_stream.getValidationState() != "published":
            data_stream.publish()
          if data_ingestion.getSimulationState() == "started":
            data_ingestion.stop()
      except Exception as e:
        context.log("ERROR stoping single ingestion: %s - reference: %s." % (data_ingestion.getId(), data_ingestion.getReference()))
        context.log(e)
  else:
    data_ingestion.deliver()

# handle split ingestions
for data_ingestion in portal_catalog(portal_type = "Data Ingestion",
                                     simulation_state = "started",
                                     id = "%"+reference_first_split):
  if not portal.ERP5Site_checkReferenceInvalidated(data_ingestion):
    if isFinishedSplitIngestion(data_ingestion.getReference()):
      try:
        query = Query(portal_type="Data Stream", reference=data_ingestion.getReference(), validation_state="draft")
        ingestion_data_stream_list = portal_catalog(query=query, sort_on=(('creation_date', 'ascending'),))
        full_file_size = 0
        for data_stream in ingestion_data_stream_list:
          full_file_size += data_stream.getSize()
          hash_value = getHash(data_stream)
          data_stream.setVersion(hash_value)
          if data_stream.getValidationState() != "validated":
            data_stream.validate()
          if data_stream.getId().endswith(reference_end_split):
            if data_stream.getValidationState() != "published":
              data_stream.publish()
            last_data_stream_id = data_stream.getId()
            #TODO: set full_file_size for EOF data stream to display the size of the full file
        related_split_ingestions = portal_catalog(portal_type = "Data Ingestion",
                                                  simulation_state = "started",
                                                  reference = data_ingestion.getReference())
        for ingestion in related_split_ingestions:
          if ingestion.getId() == last_data_stream_id:
            if ingestion.getSimulationState() == "started":
              ingestion.stop()
          else:
            ingestion.deliver()
      except Exception as e:
        context.log("ERROR handling split data streams for ingestion: %s - reference: %s." % (data_ingestion.getId(), data_ingestion.getReference()))
        context.log(e)
    else:
      if isInterruptedAbandonedSplitIngestion(data_ingestion.getReference()):
        portal.ERP5Site_invalidateSplitIngestions(data_ingestion.getReference(), success=False)
