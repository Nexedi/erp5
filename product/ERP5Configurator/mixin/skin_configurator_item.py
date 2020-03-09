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

from zLOG import LOG, INFO
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin

class SkinConfiguratorItemMixin(ConfiguratorItemMixin):
  """ Mixin which allows to create python scripts and/or skin
      elements during the configuration.
  """

  def install(self, skinfolder, business_configuration):
    """
    """
    bt5_obj = business_configuration.getSpecialiseValue()
    if bt5_obj is None:
      LOG('ConfiguratorItem', INFO,
          'Unable to find related business template to %s' % \
            business_configuration.getRelativeUrl())
      return

    template_skin_id_list = list(bt5_obj.getTemplateSkinIdList())
    if skinfolder.getId() not in template_skin_id_list:
      template_skin_id_list.append(skinfolder.getId())
    bt5_obj.edit(template_skin_id_list=template_skin_id_list)

  def _createSkinFolder(self, folder_id="custom"):
    """ Creates a new skin folder id if it do not exists and
        update Skin information """
    folder = getattr(self.portal_skins, folder_id, None)
    if folder is not None:
      return folder

    folder = self.portal_skins.manage_addProduct['OFSP'].manage_addFolder(folder_id)
    # Register on all skin selections.
    raise NotImplementedError

  def _createZODBPythonScript(self, container, script_id, script_params,
                            script_content):
    """Creates a Python script `script_id` in the given `container`, with
    `script_params` and `script_content`.

    If the container already contains an object with id `script_id`, this
    object is removed first.
    """
    if script_id in container.objectIds():
       container.manage_delObjects([script_id])

    container.manage_addProduct['PythonScripts']\
                  .manage_addPythonScript(id = script_id)
    script = container._getOb(script_id)
    script.ZPythonScript_edit(script_params, script_content)
    container.portal_url.getPortalObject().changeSkin(None)
    return script
