##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
#                    Ivan Tyagov <ivan@nexedi.com>
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

from zLOG import LOG, INFO
import time

class ConfiguratorItemMixin:
  """ This is the base class for all configurator item. """

  def install(self, document, business_configuration, prefix=''):
    """ Add object to customer customization template. """
    bt5_obj = business_configuration.getSpecialiseValue()
    if document.getPortalType() in ['Category', 'Base Category']:
      prefix = "portal_categories/"
    template_path_list = ['%s%s' % (prefix, document.getRelativeUrl()),
                          '%s%s/**' % (prefix, document.getRelativeUrl())]
    current_template_path_list = list(bt5_obj.getTemplatePathList())
    current_template_path_list.extend(template_path_list)
    bt5_obj.edit(template_path_list=current_template_path_list)

  def addToCustomerBT5ByRelativeUrl(self, business_configuration,
                                          relative_url_list):
    """ Add object to customer customization template object by
       its relative url. """
    bt5_obj = business_configuration.getSpecialiseValue()
    current_template_path_list = list(bt5_obj.getTemplatePathList())
    current_template_path_list.extend(relative_url_list)
    bt5_obj.edit(template_path_list=current_template_path_list)

  def build(self, business_configuration_relative_url):
    """ Invoke build process """
    business_configuration = self.getPortalObject().restrictedTraverse(\
       business_configuration_relative_url)
    LOG('CONFIGURATOR', INFO, 'Building --> %s' % self)
    start_build = time.time()
    result = self._build(business_configuration)
    LOG('CONFIGURATOR', INFO, 'Built    --> %s (%.02fs)' % (self,
                                     time.time()-start_build))
    return result

