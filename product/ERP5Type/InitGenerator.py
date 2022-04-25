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


from __future__ import absolute_import
import os, re, string, sys
from Products.ERP5Type import document_class_registry
from Products.ERP5Type.Globals import package_home, InitializeClass

from zLOG import LOG
import six

product_document_registry = {}
product_interactor_registry = []
interactor_class_id_registry = {}

def getProductDocumentPathList():
  return sorted((k, os.path.dirname(sys.modules[v.rsplit('.', 1)[0]].__file__))
                for k,v in six.iteritems(product_document_registry))

def InitializeDocument(class_id, class_path):
  # Register class in ERP5Type.Document
  product_document_registry[class_id] = class_path

def getProductInteractorPathList():
  return sorted(product_interactor_registry)

def InitializeInteractor(interactor_class, interactor_path=None):
  # Register class in ERP5Type.Interactor
  product_interactor_registry.append(((interactor_class, interactor_path)))

def initializeProductDocumentRegistry():
  from .Utils import importLocalDocument
  count = len(product_document_registry)
  for (class_id, class_path) in six.iteritems(product_document_registry):
    importLocalDocument(class_id, class_path=class_path)
    #from Testing import ZopeTestCase
    #ZopeTestCase._print('Added product document to ERP5Type repository: %s (%s) \n' % (class_id, document_path))
    #LOG('Added product document to ERP5Type repository: %s (%s)' % (class_id, document_path), 0, '')
    #print 'Added product document to ERP5Type repository: %s (%s)' % (class_id, document_path)
  # make sure all products are imported before we import document classes
  # (FIXME: is it true ?)
  assert count == len(product_document_registry)

def initializeProductInteractorRegistry():
  from .Utils import importLocalInteractor
  for (class_id, interactor_path) in product_interactor_registry:
    if class_id != 'Interactor': # Base class can not be global and placeless
      importLocalInteractor(class_id, path=interactor_path)

def registerInteractorClass(class_id, klass):
  interactor_class_id_registry[class_id] = klass

def installInteractorClassRegistry():
  for klass in six.itervalues(interactor_class_id_registry):
    klass().install()
