##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
#               Aurelien Calonne <aurel@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################


class BaseConduit(object):
  """
  A base class for conduit which implement the most generic methods
  and also defined methods
  It can be used as a conduit which does nothing (as a Conduit is always
  required for now even in one way mode)
  """

  def getContentType(self):
    # This must be a sub-BaseConduit
    return "text/xml"

  def generateDiff(self, new_data, former_data):
    return None

  def getXMLFromObjectWithId(self, object, xml_mapping, context_document=None): # pylint: disable=redefined-builtin
    """
      return the xml with Id of Object
    """
    # XXX to be renamed
    data = ''
    if not xml_mapping:
      return data
    data_generator_method = getattr(object, xml_mapping, None)
    if data_generator_method:
      try:
        data = data_generator_method(context_document=context_document)
      except TypeError:
        # The method does not accept parameters (ie old-style)
        data = data_generator_method()
    return data


  def getGidFromObject(self, object): # pylint: disable=redefined-builtin
    """
    return the Gid composed with the object informations
    """
    # XXX to be renamed
    return object.getId()


  def replaceIdFromXML(self, xml, attribute_name, new_id, as_string=True):
    # XXX To be renamed & review
    return xml

  def addNode(self, *args, **kw):
    """
    Method call when a add command is received
    It returns the list of conflict as well as the newly created document
    This has to be reviewed,  object is not required anylonger
    """
    return {'conflict_list': [], 'object': None}

  def updateNode(self, *args, **kw):
    """
    Method called when update command is received
    It returns the list of conflicts
    """
    return []

  def deleteNode(self, *args, **kw):
    """
    Method called when update command is received
    XXX It should returns the list of conflicts ?
    """

