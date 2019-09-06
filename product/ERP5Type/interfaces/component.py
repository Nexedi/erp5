# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from zope.interface import Interface

class IComponent(Interface):
  """
  ZODB Component interface. Component were previously defined on the
  filesystem and are now defined in portal_components and can be bt5
  Extensions or Documents, or any interfaces, mixin and Documents from
  Products. Any Component class must implement this interface
  """
  def _hookAfterLoad(self, module_obj):
    """
    Idempotent hook called after loading the module
    """
    pass

  def checkConsistency(obj, *args, **kwargs):
    """
    Check the consistency of a ZODB Component when validating from draft state
    (manual user action) or when modified while already validated beforehand
    """

  def checkConsistencyAndValidate(obj):
    """
    After a previously validated Component is modified, check the consistency,
    then if no error is returned, validate it
    """

  def checkSourceCode(self):
    """
    Check source code statically
    """

  def _getFilesystemPath():
    """
    Return the filesystem Component path for import into ZODB
    """

  def _getDynamicModuleNamespace():
    """
    Return the module name where Component module are loaded into
    """

  def getIdPrefix():
    """
    Return the ID prefix for Component objects
    """

  def importFromFilesystem(cls,
                           context,
                           reference,
                           version,
                           source_reference=None,
                           filesystem_zodb_module_mapping_set=None):
    """
    Import a Component from the filesystem into ZODB after checking that the
    source code is valid
    """
