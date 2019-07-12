from Products.ERP5Type.Log import log
from Products.ZSQLCatalog.SQLCatalog import Query, SimpleQuery
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
    except:
      # data stream is empty
      data_stream_chunk = ""
    hash_md5.update(data_stream_chunk)
    if data_stream_chunk == "": break
    n_chunk += 1
  return hash_md5.hexdigest()

def isInterruptedAbandonedSplitIngestion(reference):
  from DateTime import DateTime
  now = DateTime()
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

reference_end_single = portal.getIngestionReferenceDictionary()["single_end_suffix"]
reference_first_split = portal.getIngestionReferenceDictionary()["split_first_suffix"]
reference_end_split = portal.getIngestionReferenceDictionary()["split_end_suffix"]

# stop single started ingestion (not split files)
for data_ingestion in portal_catalog(portal_type = "Data Ingestion",
                                     simulation_state = "started",
                                     id = "%"+reference_end_single):
  if not portal.IsReferenceInvalidated(data_ingestion):
    related_split_ingestions = portal_catalog(portal_type = "Data Ingestion",
                                              reference = data_ingestion.getReference())
    if len(related_split_ingestions) == 1:
      data_stream = portal_catalog.getResultValue(
        portal_type = 'Data Stream',
        reference = data_ingestion.getReference())
      if data_stream is not None:
        hash_value = getHash(data_stream)
        data_stream.setVersion(hash_value)
        if data_stream.getValidationState() != "validated":
          data_stream.validate()
        if data_ingestion.getSimulationState() == "started":
          data_ingestion.stop()

# append split ingestions
for data_ingestion in portal_catalog(portal_type = "Data Ingestion",
                                     simulation_state = "started",
                                     id = "%"+reference_first_split):
  if not portal.IsReferenceInvalidated(data_ingestion):
    if isInterruptedAbandonedSplitIngestion(data_ingestion.getReference()):
      portal.ERP5Site_invalidateSplitIngestions(data_ingestion.getReference(), success=False)
    else:
      try:
        last_data_stream_id = ""
        query = Query(portal_type="Data Stream", reference=data_ingestion.getReference(), validation_state="draft")
        result_list = portal_catalog(query=query, sort_on=(('creation_date', 'ascending'),))
        full_data_stream = None
        for data_stream in result_list:
          log(''.join(["Data stream for split ingestion: ", data_stream.getId()]))
          if data_stream.getId() == data_ingestion.getId():
            log("It is base data stream")
            full_data_stream = data_stream
          else:
            log("It is not base data stream, it is a part")
            if full_data_stream != None:
              log("appending content to base data stream...")
              full_data_stream.appendData(data_stream.getData())
              last_data_stream_id = data_stream.getId()
              portal.data_stream_module.deleteContent(data_stream.getId())
        if last_data_stream_id.endswith(reference_end_split):
          portal.ERP5Site_invalidateSplitIngestions(data_ingestion.getReference(), success=True)
          hash = getHash(full_data_stream)
          full_data_stream.setVersion(hash)
          if full_data_stream.getValidationState() != "validated":
            full_data_stream.validate()
          related_split_ingestions = portal_catalog(portal_type = "Data Ingestion",
                                                    simulation_state = "started",
                                                    reference = data_ingestion.getReference())
          for ingestion in related_split_ingestions:
            if ingestion.getId() == full_data_stream.getId():
              if ingestion.getSimulationState() == "started":
                ingestion.stop()
            else:
              portal.InvalidateReference(ingestion)
              ingestion.deliver()
      except Exception as e:
        context.logEntry("ERROR appending split data streams for ingestion: %s - reference: %s." % (data_ingestion.getId(), data_ingestion.getReference()))
        context.logEntry(e)
