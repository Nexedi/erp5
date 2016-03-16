"""
when OOoDocument is edited, we update metadata in the ODF file

XXX - This script must be verified, written with clean syntax
"""
document = state_change['object']
kw = state_change['kwargs']

# key is a name of erp5 field.
# value is a name of document metadata.
metadata_field_mapping_dict = document.getMetadataMappingDict()

# edit metadata (only if we have OOo file)
if document.hasBaseData():
  new_metadata = {}
  for field in metadata_field_mapping_dict.keys():
    value = kw.get(field, None)
    if value is None:
      value = kw.get('%s_list' % field, None)
    if value is not None:
      metadata_key = metadata_field_mapping_dict[field]
      new_metadata[metadata_key] = value
  if new_metadata:
    # edit metadata via server
    after_tag = 'document_%s_convert' % document.getPath()
    document.activate(after_tag=after_tag).Document_tryToUpdateBaseMetadata(**new_metadata)
