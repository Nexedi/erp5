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

import os,string
from os import access,W_OK

# We first should look to the export folder
base_directory_path = '/mnt/edi'
export_directory_path = os.path.join(base_directory_path, 'Depart')

def exportEdiAuchanFile(self, user_name=None, ending_mail=0):
  import os, string
  from os import access,W_OK

  file_name = 'exportEdiAuchan_' + self.getId() + '.env'
  file_path = os.path.join(export_directory_path, file_name)

  try:
    resultTmp = self.SalesPackingList_exportEdiAuchan( batch_mode=1 )
  except:
    self.Coramy_sendMailToUser(user_name=user_name,mSubj="Erreur d exécution, export Edi annulé",mMsg=file_path)
  else:

    try:
      # open the file
      file = open( file_path , 'w')
    except:
      self.Coramy_sendMailToUser(user_name=user_name,mSubj="Impossible d ouvrir le fichier Edi : contactez Romain",mMsg=file_path)

    try:
      # export the file
      file.write( resultTmp )
    except:
      self.Coramy_sendMailToUser(user_name=user_name,mSubj="Impossible d écrire le fichier Edi : contactez Romain",mMsg=file_path)

    try:
      # close
      file.close()
    except:
      self.Coramy_sendMailToUser(user_name=user_name,mSubj="Impossible de fermer le fichier Edi : contactez Romain",mMsg=file_path)
      
  if ending_mail:
    mMsg = ''
    self.Coramy_sendMailToUser(user_name=user_name,mSubj="Export de l edi Auchan terminé",mMsg=mMsg)


"""
test the directory 
"""
def exportEdiAuchanTestDirectory(self ):
  import os, string
  from os import access,W_OK
  
  # test the directory
  return access(export_directory_path, W_OK)

