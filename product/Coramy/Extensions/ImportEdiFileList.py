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

#if not os.path.exists(import_directory_path ):
#  os.mkdir( import_directory_path )


def importEdiFile(self, file_path=None, delivery_mode=None, incoterm=None, order_type=None, segmentation_strategique=None, travel_duration=None, user_name=None):
  import os, string
  from DateTime import DateTime
  from ZPublisher.HTTPRequest import FileUpload
  from cgi import FieldStorage
  from os import access,W_OK


  try:
    # open the file
    file = open( file_path , 'r')
  except:
    self.Coramy_sendMailToUser(user_name=user_name,mSubj="Impossible d ouvrir le fichier Edi",mMsg=file_path)
    
  try:
    # create the correct parameter
    form=FieldStorage()
    form.filename = file_path
    form.file = file
    import_file = FileUpload(form)
  except:
    self.Coramy_sendMailToUser(user_name=user_name,mSubj="Impossible de lire le fichier Edi",mMsg=file_path)

  else:
    
    if access(file_path, W_OK):
      try:
        
        # import the file
        resultTmp = self.SalesOrder_importEdi(import_file=import_file, delivery_mode=delivery_mode, incoterm=incoterm, order_type=order_type, segmentation_strategique=segmentation_strategique, travel_duration=travel_duration, batch_mode=1,user_name=user_name)

      except:
        self.Coramy_sendMailToUser(user_name=user_name,mSubj="Erreur d execution, import Edi annulé",mMsg=file_path)
      else:
        # test the result
        file.close()
        if resultTmp[1] == None:
          self.Coramy_sendMailToUser(user_name=user_name,mSubj="Fichier non valide, import Edi annulé",mMsg=file_path)
        else:
          #self.Coramy_sendMailToUser(user_name=user_name,mSubj="Import réussi",mMsg=resultTmp[0])
          #get_transaction().commit()
          os.remove(file_path)


    else:
      file.close()
      self.Coramy_sendMailToUser(user_name=user_name,mSubj="Impossible d effacer le fichier Edi, import annulé",mMsg=file_path)

"""
test the directory and creation of all the messages
"""
def importEdiFileListTestAndStart(self, delivery_mode=None, incoterm=None, order_type=None, segmentation_strategique=None, travel_duration=None, user_name=None ):
  import os, string
  from DateTime import DateTime
  from ZPublisher.HTTPRequest import FileUpload
  from cgi import FieldStorage
  from os import access,W_OK
  
  # test the directory
  if access(import_directory_path, W_OK):
    #self.Coramy_sendMailToUser(user_name=user_name,mSubj="Lancement de l import en masse ",mMsg=import_directory_path)

    files_list = os.listdir(import_directory_path)

    for file_name in files_list:
      file_path = os.path.join(import_directory_path, file_name)

      self.activate(activity="SQLQueue", priority=4).SalesOrder_importEdiFile(file_path=file_path, delivery_mode=delivery_mode, incoterm=incoterm, order_type=order_type, segmentation_strategique=segmentation_strategique, travel_duration=travel_duration, user_name=user_name )
      

  else:
    self.Coramy_sendMailToUser(user_name=user_name,mSubj="Impossible d ecrire sur le repertoire d import, import annule",mMsg=import_directory_path)

"""
this allows to import many edi files at the same time
no more used
"""
"""
def importEdiFileList(self, REQUEST,file_path=None, delivery_mode=None, incoterm=None, order_type=None, segmentation_strategique=None, travel_duration=None, batch_mode=0):

  user_name = self.portal_membership.getAuthenticatedMember().getUserName()
  # test the directory
  # can't be good, because this test is done on TinyLeon, and the message is done on SumicomA
  if access(import_directory_path, W_OK):

    files_list = os.listdir(import_directory_path)

    for file_name in files_list:
      file_path = os.path.join(import_directory_path, file_name)

      self.activate(activity="SQLQueue").SalesOrder_importEdiFile(file_path=file_path, delivery_mode=delivery_mode, incoterm=incoterm, order_type=order_type, segmentation_strategique=segmentation_strategique, travel_duration=travel_duration, user_name=user_name )
      
    redirect_url = '%s?%s' % ( self.absolute_url()+'/'+'view', 'portal_status_message=Import+des+fichiers+EDI+lancé.')

  else:
    redirect_url = '%s?%s%s' % ( self.absolute_url()+'/'+'view', "portal_status_message=Annulation:+impossible+d+écrire+sur+le+répertoire+d'import+",import_directory_path)


  if batch_mode:
    return None
  else:
    REQUEST[ 'RESPONSE' ].redirect( redirect_url )
"""
