"""
  Script to check that a filesystem md5sum of a folder (uploaded to file_system_checksum File)
  is properly uploaded to Wendelin Data Lake.

  Format of is the same as md5sum's output:
  <md5_sum>    <filename.extension>

"""

data =  str(context.file_system_checksum).strip()
lines = data.split("\n")
print "Total files = ", len(lines)
for line in lines[:]:
  md5_checksum = line[:32].strip()
  full_filename = line[32:].strip()

  # check Data stream for this hash exists
  filename, extension = full_filename.split(".")
  reference = "%s/%s/%s" %(data_set_reference, filename, extension)
  catalog_kw = {"portal_type": "Data Stream",
                "reference": reference}
  data_stream = context.portal_catalog.getResultValue(**catalog_kw)
  if data_stream is None:
    print "[NOT FOUND]", reference
  else:
    is_upload_ok = (data_stream.getVersion()==md5_checksum)
    print md5_checksum, filename, data_stream is not None, is_upload_ok

return printed
