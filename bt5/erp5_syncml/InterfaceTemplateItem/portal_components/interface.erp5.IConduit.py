# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#          Fabien Morin <fabien.morin@gmail.com>
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

from zope.interface import Interface

class IConduit(Interface):
  """
    A conduit is a piece of code in charge of

    - updating an object attributes from an XUpdate XML stream

    (Conduits are not in charge of creating new objects which
    are eventually missing in a synchronization process)

    If an object has be created during a synchronization process,
    the way to proceed consists in:

    1- creating an empty instance of the appropriate class
      in the appropriate directory

    2- updating that empty instance with the conduit

    The first implementation of ERP5 synchronization
    will define a default location to create new objects and
    a default class. This will be defined at the level of the synchronization
    tool

    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx
    Look carefully when we are adding elements,
    for example, when we do 'insert-after', with 2 xupdate:element,
    so adding 2 differents objects, actually it adds only XXXX one XXX object
    In this case the getSubObjectDepth(), doesn't have
    too much sence
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    There is also one problem, when we synchronize a conflict,
    we are not waiting
    the response of the client, so that we are not sure if it take into account,
    we may have CONFLICT_NOT_SYNCHRONIZED AND CONFLICT_SYNCHRONIZED
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  """

  def constructContent(object, object_id, portal_type): # pylint: disable=redefined-builtin
    """
    This allows to specify how to construct a new content.
    This is really usefull if you want to write your
    own Conduit.

    object: from where new content is created

    object_id: id of the new object

    portal_type: portal_type of the new object

    return newObject, reset_local_roles boolean, reset_workflow boolean
    """

  def addNode(xml=None, object=None, previous_xml=None, # pylint: disable=redefined-builtin
              object_id=None, sub_object=None, force=0, simulate=0, **kw):
    """
    A node is added

    xml : the xml wich contains what we want to add

    object : from where we want to add something

    previous_xml : the previous xml of the object, if any

    force : apply updates even if there's a conflict

    This fucntion returns conflict_list, wich is of the form,
    [conflict1,conflict2,...] where conclict1 is of the form :
    [object.getPath(),keyword,local_and_actual_value,subscriber_value]
    """

  def deleteNode(xml=None, object=None, object_id=None, force=None, # pylint: disable=redefined-builtin
                 simulate=0, **kw):
    """
    A node is deleted
    """

  def updateNode(xml=None, object=None, previous_xml=None, force=0, # pylint: disable=redefined-builtin
                 simulate=0,  **kw):
    """
    A node is updated with some xupdate
      - xml : the xml corresponding to the update, it should be xupdate
      - object : the object on wich we want to apply the xupdate
      - [previous_xml] : the previous xml of the object, it is mandatory
                         when we have sub objects

    """

  def getGidFromObject(object, configurable_gid_dictionary=None): # pylint: disable=redefined-builtin
    """
    return the Gid composed with the object information
     - object is the document on which for we are building the gid.
       It is usefull to interogate properties of this document itself.
     - configurable_gid_dictionary optional argument which is supposed to be a dictionary
     with parameters usefull to build the GID.
       property_list = ordered_list of properties to interrogate
       prefix = string to add in first place of the outputted string
       safe = True or False. True means raise an error if interrogated property is
       empty or doesn't exists.
       if generated GID is empty an error is allways raised
    """

  def getGidFromXML(xml, namespace, gid_from_xml_list):
    """
    return the Gid composed with xml information
    """

  def applyDiff(original_data, diff):
    """Patch original data with given diff
    and return patched data

    original_data - can be plain/text or text/xml data
    diff - diff generated with difflib or xupdate
    """

  def generateDiff(old_data, new_data):
    """return a diff between old_data and new_data
    respecting mimetype of handled data.
    text/xml => xupdate
    plain/text => difflib
    """
