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
from os import access,W_OK

# We first should look to the import folder
base_directory_path = '/mnt/edi'
import_directory_path = os.path.join(base_directory_path, 'Arrivee')
log_directory_path = base_directory_path

if not os.path.exists(import_directory_path ):
  os.mkdir( import_directory_path )
if not os.path.exists(log_directory_path ):
  os.mkdir( log_directory_path )


def importEdiFile(object=None, file_path=None, delivery_mode=None, incoterm=None, order_type=None, segmentation_strategique=None, travel_duration=None):

  resultTab = [] 
  
  result = ''
  result = result +  '\n--------------------------------------------\n'
  result = result + file_path + '\n'
  result = result + DateTime().strftime("%a, %Y %B %d %H:%M:%S")

  if access(file_path, W_OK):
    
    # open the file
    file = open( file_path , 'r')

    # create the correct parameter
    form=FieldStorage()
    form.filename = file_path
    form.file = file
    import_file = FileUpload(form)

    # import the file
    resultTmp = object.SalesOrder_importEdi(import_file=import_file, delivery_mode=delivery_mode, incoterm=incoterm, order_type=order_type, segmentation_strategique=segmentation_strategique, travel_duration=travel_duration, batch_mode=1)

    file.close()

    # test the result
    if resultTmp == None:
      result = result + '\n' + 'Fichier non valide\n'
      resultTab += [(0,result)]
    else:
      result = result + '\n' +  resultTmp
      os.remove(file_path)
      resultTab += [(1,result)]


  else:
    result += '\nPas d acces en ecriture\n'
    resultTab += [(0,result)]


  return resultTab


"""
this allows to import many edi files by the same time
"""
def importEdiFileList(self, REQUEST,file_path=None, delivery_mode=None, incoterm=None, order_type=None, segmentation_strategique=None, travel_duration=None, batch_mode=0):
	
  result = ''
  result += '##############################################################################   \n'
  result += 'Tentative d import\n'+ DateTime().strftime("%a, %Y %B %d %H:%M:%S")+'\n'
  result += '##############################################################################   \n'

  edi_files_number = 0

  # test the log file
  if access(log_directory_path, W_OK):

    files_list = os.listdir(import_directory_path)


    tab = []

    for file_name in files_list:
      file_path = os.path.join(import_directory_path, file_name)
    
      tab += importEdiFile(object=self, file_path=file_path, delivery_mode=delivery_mode, incoterm=incoterm, order_type=order_type, segmentation_strategique=segmentation_strategique, travel_duration=travel_duration ) 


    
    for comment in tab: 
      if comment[0]:
     	edi_files_number += 1 
      result += comment[1]

    # write the log file
    log_path = os.path.join(log_directory_path, 'importEdiERP5.log')
    log_file = open(log_path,'a')
    log_file.write(result)
    log_file.close()

  else:
    result += 'Ne peut ecrire le fichier de log\n'


  if batch_mode:
    return result
  else:
    redirect_url = '%s?%s%i%s' % ( self.absolute_url()+'/'+'view', 'portal_status_message=',edi_files_number ,' Fichiers+EDI+importés.')
    REQUEST[ 'RESPONSE' ].redirect( redirect_url )
