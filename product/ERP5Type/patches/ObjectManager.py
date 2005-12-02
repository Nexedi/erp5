##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

# Import: add rename feature
from OFS.ObjectManager import ObjectManager, customImporters

def ObjectManager_importObjectFromFile(self, filepath, verify=1, set_owner=1, id=None):
    #LOG('_importObjectFromFile, filepath',0,filepath)
    # locate a valid connection
    connection=self._p_jar
    obj=self

    while connection is None:
        obj=obj.aq_parent
        connection=obj._p_jar
    ob=connection.importFile(
        filepath, customImporters=customImporters)
    if verify: self._verifyObjectPaste(ob, validate_src=0)
    if id is None:
      id=ob.id
    if hasattr(id, 'im_func'): id=id()
    self._setObject(id, ob, set_owner=set_owner)

    # try to make ownership implicit if possible in the context
    # that the object was imported into.
    ob=self._getOb(id)
    ob.manage_changeOwnershipType(explicit=0)

ObjectManager._importObjectFromFile=ObjectManager_importObjectFromFile
