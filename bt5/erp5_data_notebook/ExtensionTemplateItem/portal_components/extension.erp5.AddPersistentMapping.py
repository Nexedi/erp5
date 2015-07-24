# -*- coding: utf-8 -*-

from Products.ERP5Type.Globals import  PersistentMapping

def AddPersistentMapping(self):
  """
  Function to add PersistentMapping object which can be used as a dictionary
  """
  new_dict = PersistentMapping()
  return new_dict

def UpdatePersistentMapping(self, existing_dict):
  """
  Function to update PersistentMapping object
  """
  new_dict = PersistentMapping()
  for key, value in existing_dict.iteritems():
    new_dict[key]=value
  return new_dict