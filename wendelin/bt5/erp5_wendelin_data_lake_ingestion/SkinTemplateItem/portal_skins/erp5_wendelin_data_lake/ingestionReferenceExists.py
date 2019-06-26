from DateTime import DateTime
from Products.ERP5Type.Log import log

# reference parameter example: supplier/dataset/filename/fif/EOF/size/hash
# ingestion reference example: dataset/filename/fif

FALSE = "FALSE"
TRUE = "TRUE"

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

reference_separator = portal.getIngestionReferenceDictionary()["reference_separator"]
reference_end_single = portal.getIngestionReferenceDictionary()["single_end_suffix"]
reference_end_split = portal.getIngestionReferenceDictionary()["split_end_suffix"]

try:
  # remove supplier and eof from reference
  data_ingestion_reference = reference_separator.join(reference.split(reference_separator)[1:-3])
  EOF = reference.split(reference_separator)[-3]
  size = reference.split(reference_separator)[-2]

  if data_ingestion_reference is "":
    context.logEntry("[ERROR] Data Ingestion reference parameter for ingestionReferenceExists script is not well formated")
    raise ValueError("Data Ingestion reference is not well formated")

  # check if there are started ingestions for this reference
  data_ingestion = portal_catalog.getResultValue(
    portal_type = 'Data Ingestion',
    simulation_state = "started",
    reference = data_ingestion_reference)
  if data_ingestion != None:
    try:
      # check if user tries to restart the previous split ingestion
      if (EOF == "" or EOF == reference_end_single) or (EOF != reference_end_split and int(EOF) == 1):
        # check if existing split ingestion is still being processed or if it is interrumped
        data_ingestion_eof = portal_catalog.getResultValue(
          portal_type = 'Data Ingestion',
          reference = data_ingestion_reference,
          id = "%" + reference_end_split)
        if data_ingestion_eof:
          # reference exists: previous split ingestion is still being processed
          return TRUE
        else:
          # previous ingestion was interrumped
          log(''.join(["[WARNING] User has restarted an interrumpted ingestion for reference ", data_ingestion.getReference(), ". Previous split ingestions will be discarted and full ingestion restarted."]))
          portal.ERP5Site_invalidateSplitIngestions(data_ingestion.getReference(), success=False)
    except:
      pass
    # the ingestion attemp corresponds to a split ingestion in course, accept
    return FALSE

  data_ingestion = portal_catalog.getResultValue(
    portal_type = 'Data Ingestion',
    reference = data_ingestion_reference)

  if data_ingestion is None:
    return FALSE

  # TODO: fix this (contemplate scenarios of partial ingestion overwrites)
  if size != "" and size != None:
    # this is a modified file
    return FALSE
  return TRUE
except Exception as e:
  context.logEntry(''.join(["[ERROR] At script ingestionReferenceExists: ", str(e)]))
  raise e
