"""
  Script to check that a data set is properly uploaded
  to Wendelin Data Lake.

  How to use it: create a file_system_checksum file containing md5sum
  values of all dataset files uploaded with the following format:

  Format of is the same as md5sum's output:
  <md5_sum>    <filename.extension>

  It can be generated in the original data set folder outside wendelin by doing md5sum * > output.txt
"""

import os.path
data =  str(context.file_system_checksum).strip()
lines = data.split("\n")
print "Total files = ", len(lines)
print
check_result = True
for line in lines[:]:
  md5_checksum = line[:32].strip()
  full_filename = line[32:].strip()
  filename, extension = os.path.splitext(full_filename)
  extension = extension[1:]
  reference = "%s/%s/%s" %(data_set_reference, filename, extension)
  catalog_kw = {"portal_type": "Data Stream",
                "reference": reference}
  data_stream = context.portal_catalog.getResultValue(**catalog_kw)
  if data_stream is None:
    print "[NOT FOUND]", reference
    check_result = False
  else:
    is_upload_ok = (data_stream.getVersion()==md5_checksum)
    print md5_checksum, filename, data_stream is not None, is_upload_ok
    if not is_upload_ok:
      check_result = False
print
if check_result:
  print "[OK] Data set correctly uploaded"
else:
  print "[ERROR] Data set was not correctly uploaded"
return printed
