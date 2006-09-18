##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
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

"""Utility functions and classes for unit testing
"""

from Products.MailHost.MailHost import MailHost

class DummyMailHost(MailHost):
  """Dummy Mail Host that doesn't really send messages and keep a copy in
  _last_message attrbute.
  To use it, you have to replace existing mailhost in afterSetUp:
    
    if 'MailHost' in portal.objectIds():
      portal.manage_delObjects(['MailHost'])
    portal._setObject('MailHost', DummyMailHost('MailHost'))
  """
  _last_message = ()
  def _send( self, mfrom, mto, messageText ):
    """Record message in _last_message."""
    self._last_message = (mfrom, mto, messageText)

def createZODBPythonScript(container, script_id, script_params,
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
  script = container[script_id]
  script.ZPythonScript_edit(script_params, script_content)
  container.portal_url.getPortalObject().changeSkin(None)
  return script

def removeZODBPythonScript(container, script_id):
  """
  Removes a Python script `script_id` in the given `container`.
  """
  container.manage_delObjects([script_id])
