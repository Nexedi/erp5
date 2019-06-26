portal = context.getPortalObject()
portal_catalog = portal.portal_catalog
reference_separator = portal.getIngestionReferenceDictionary()["reference_separator"]
none_extension = portal.getIngestionReferenceDictionary()["none_extension"]

# check new reference
data_ingestions = portal_catalog(portal_type = "Data Ingestion", reference = new_reference)
if len(data_ingestions) > 0: raise "Error renaming: new reference '%s' already exists." % new_reference

# rename data ingestions
data_ingestions = portal_catalog(portal_type = "Data Ingestion", reference = reference)
if len(data_ingestions) == 0: raise "Error renaming: could not find any data ingestion with reference '%s'." % reference
data_ingestion_title = reference_separator.join(new_reference.split(reference_separator)[1:-1])
for data_ingestion in data_ingestions:
  data_ingestion.setReference(new_reference)
  data_ingestion.setTitle(data_ingestion_title)

extension = new_reference.split(reference_separator)[-1]
data_stream_title = "%s%s" % (data_ingestion_title, "."+extension if extension != none_extension else "")
# rename data streams
data_streams = portal_catalog(portal_type = "Data Stream", reference = reference)
for data_stream in data_streams:
  data_stream.setReference(new_reference)
  data_stream.setTitle(data_stream_title)

# rename data analysis
data_analysises = portal_catalog(portal_type = "Data Analysis", reference = reference)
for data_analysis in data_analysises:
  data_analysis.setReference(new_reference)

# rename data arrays
data_arrays = portal_catalog(portal_type = "Data Array", reference = reference)
for data_array in data_arrays:
  data_array.setReference(new_reference)
