# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Sebastien Robin <seb@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


import os, re, string, sys
from Globals import package_home, InitializeClass

from zLOG import LOG

global product_document_registry
product_document_registry = []
global product_interactor_registry
product_interactor_registry = []
global interactor_class_id_registry 
interactor_class_id_registry = {}

def getProductDocumentPathList():
  result = product_document_registry
  result.sort()
  return result

def InitializeDocument(document_class, document_path=None):
  global product_document_registry
  # Register class in ERP5Type.Document
  product_document_registry.append(((document_class, document_path)))

def getProductInteractorPathList():
  result = product_interactor_registry
  result.sort()
  return result

def InitializeInteractor(interactor_class, interactor_path=None):
  global product_interactor_registry
  # Register class in ERP5Type.Interactor
  product_interactor_registry.append(((interactor_class, interactor_path)))

def initializeProductDocumentRegistry():
  from Utils import importLocalDocument
  for (class_id, document_path) in product_document_registry:
    importLocalDocument(class_id, document_path=document_path)
    #from Testing import ZopeTestCase
    #ZopeTestCase._print('Added product document to ERP5Type repository: %s (%s) \n' % (class_id, document_path))
    #LOG('Added product document to ERP5Type repository: %s (%s)' % (class_id, document_path), 0, '')
    #print 'Added product document to ERP5Type repository: %s (%s)' % (class_id, document_path)
    
def initializeProductInteractorRegistry():
  from Utils import importLocalInteractor
  for (class_id, interactor_path) in product_interactor_registry:
    if class_id != 'Interactor': # Base class can not be global and placeless
      importLocalInteractor(class_id, path=interactor_path)

def registerInteractorClass(class_id, klass):
  global interactor_class_id_registry
  interactor_class_id_registry[class_id] = klass

def installInteractorClassRegistry():
  global interactor_class_id_registry
  for class_id, klass in interactor_class_id_registry.items():
    klass().install()
