##############################################################################
#
# Copyright (c) 2003 Coramy SAS and Contributors. All Rights Reserved.
#                    Romain Courteaud <Romain_Courteaud@coramy.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
#
# This program as such is not intended to be used by end users. End
# users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the Zope Public License (ZPL) Version 2.0
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os, string
from DateTime import DateTime
from ZPublisher.HTTPRequest import FileUpload
from cgi import FieldStorage

# We first should look to the import folder
base_directory_path = '/mnt/edi'
import_directory_path = os.path.join(base_directory_path, 'Arrivee')
log_directory_path = base_directory_path

if not os.path.exists(import_directory_path ):
  os.mkdir( import_directory_path )
if not os.path.exists(log_directory_path ):
  os.mkdir( log_directory_path )


"""
this allows to import many edi files by the same time
"""
def importEdiFiles(self, REQUEST, delivery_mode, incoterm, order_type, segmentation_strategique, travel_duration):

  files_list = os.listdir(import_directory_path)
  result = ''
  edi_files_number = 0
  for file_name in files_list:

    file_path = os.path.join(import_directory_path, file_name)
    
    result = result +  '\n##############################################################################   \n'
    result = result + file_path + '\n'
    result = result + DateTime().strftime("%a, %Y %B %d %H:%M:%S")
    #result = result + DateTime().asctime()
    
    # open the file
    file = open( file_path   , 'r')

    # create the correct parameter
    form=FieldStorage()
    form.filename = file_path
    form.file = file
    import_file = FileUpload(form)

    # import the file
    resultTmp = self.SalesOrder_importEdi(import_file=import_file, delivery_mode=delivery_mode, incoterm=incoterm, order_type=order_type, segmentation_strategique=segmentation_strategique, travel_duration=travel_duration)

    # test the result
    if resultTmp == None:
      result = result + '\n'
      file.close()
    else:
      edi_files_number += 1
      result = result + '\n' +  resultTmp
      file.close()
      os.remove(file_path)


  # write the log file
  log_path = os.path.join(log_directory_path, 'importEdiERP5.log')
  log_file = open(log_path,'a')
  log_file.write(result)
  log_file.close()

  redirect_url = '%s?%s%i%s' % ( self.absolute_url()+'/'+'view', 'portal_status_message=',edi_files_number ,' Fichiers+EDI+importés.')
  REQUEST[ 'RESPONSE' ].redirect( redirect_url )
