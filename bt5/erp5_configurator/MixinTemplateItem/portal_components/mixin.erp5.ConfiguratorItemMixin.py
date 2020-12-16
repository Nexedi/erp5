##############################################################################
#
# Copyright (c) 2006-2012 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
#                    Ivan Tyagov <ivan@nexedi.com>
#                    Rafael Monnerat <rafael@nexedi.com>
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

from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage
from zLOG import LOG, INFO

class ConfiguratorItemMixin:
  """ This is the base class for all configurator item. """

  def getBusinessConfigurationValue(self):
    item = self
    while item.getPortalType() != 'Business Configuration':
      item = item.getParentValue()
    return item

  def _createConstraintMessage(self, message):
    return ConsistencyMessage(self,
        object_relative_url=self.getRelativeUrl(),
        message=message)

  def install(self, document, business_configuration, prefix=''):
    """ Add object to customer customization template. """
    bt5_obj = business_configuration.getSpecialiseValue()
    if bt5_obj is None:
      LOG('ConfiguratorItem', INFO,
          'Unable to find related business template to %s' % \
            business_configuration.getRelativeUrl())
      return

    if document.getPortalType() in ['Category', 'Base Category']:
      prefix = "portal_categories/"
    template_path_list = ['%s%s' % (prefix, document.getRelativeUrl()),
                          '%s%s/**' % (prefix, document.getRelativeUrl())]

    current_template_path_list = list(bt5_obj.getTemplatePathList())
    current_template_path_list.extend(template_path_list)
    bt5_obj.edit(template_path_list=current_template_path_list)
