# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Products.ERP5Type.Interactor.Interactor import Interactor

class FieldValueCacheInteractor(Interactor):

  def install(self):
    """
      Installs interactions
    """
    from Products.Formulator.Field import ZMIField
    from Products.ERP5Form.ProxyField import ProxyField
    from Products.Formulator.Form import ZMIForm
    self.on(ZMIField, 'manage_edit').doAfter(self.purgeFieldValueCache)
    self.on(ZMIField, 'manage_edit_xmlrpc').doAfter(self.purgeFieldValueCache)
    self.on(ZMIField, 'manage_tales').doAfter(self.purgeFieldValueCache)
    self.on(ZMIField, 'manage_tales_xmlrpc').doAfter(self.purgeFieldValueCache)
    self.on(ProxyField, 'manage_edit').doAfter(self.purgeFieldValueCache)
    self.on(ProxyField, 'manage_edit_target').doAfter(self.purgeFieldValueCache)
    self.on(ProxyField, 'manage_tales').doAfter(self.purgeFieldValueCache)
    self.on(ZMIForm, 'manage_renameObject').doAfter(self.purgeFieldValueCache)

  def purgeFieldValueCache(self, method_call_object):
    """
      Interaction method (defined at the Interactor level).
      Make sure all field value caches are purged
    """
    from Products.ERP5Form.Form import field_value_cache
    field_value_cache.clear()
