portal = context.getPortalObject()
reference_separator = portal.getIngestionReferenceDictionary()["reference_separator"]
reference_length = portal.getIngestionReferenceDictionary()["reference_length"]
invalid_chars = portal.getIngestionReferenceDictionary()["invalid_chars"]

record = reference.rsplit(reference_separator)
length = len(record)

if (length < reference_length):
  context.logEntry("[ERROR] In HandleFifEmbulkIngestion: Data Ingestion reference is not well formated")
  raise ValueError("Data Ingestion reference is not well formated.")

for char in invalid_chars:
    if char in reference:
      context.logEntry("[ERROR] In HandleFifEmbulkIngestion: Data Ingestion reference contains chars that are not allowed")
      raise ValueError("Data Ingestion reference contains chars that are not allowed.")


supplier = record[0]
dataset_reference = record[1]
filename = reference_separator.join(record[2:-4])
extension = record[length-4]
eof = record[length-3]
size = record[length-2]
hash = record[length-1]

dict = { 'filename': filename,
         'extension': extension,
         'eof': eof,
         'supplier': supplier,
         'dataset_reference': dataset_reference,
         'resource_reference': 'fif',
         'size': size,
         'hash': hash
       }

return dict
