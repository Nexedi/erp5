##############################################################################
#
# Base18: a Zope product which provides multilingual services for CMF Default
#         documents.
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
#
# This program as such is not intended to be used by end users. End
# users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the Zope Public License (ZPL) Version 2.0
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
    Converts instances of Products.CMFDefault.<content> to
    instances of Products.Base18.<content>.
"""

# Source
import Products.CMFDefault.NewsItem
import Products.CMFDefault.Link
import Products.CMFDefault.Document
import Products.CMFDefault.File
import Products.CMFDefault.Image
import Products.CMFDefault.DiscussionItem
import Products.CMFDefault.Favorite
import Products.CMFCore.PortalFolder

# Destination
import Products.Base18.NewsItem
import Products.Base18.Replica
import Products.Base18.Document

#
import re
from zLOG import LOG

migrations = {
    Products.CMFDefault.Document.Document               :\
              Products.Base18.Document.Document18,
    Products.CMFDefault.NewsItem.NewsItem               :\
              Products.Base18.NewsItem.NewsItem18,
    Products.CMFDefault.Link.Link                       :\
              Products.Base18.Replica.Link18,
    Products.CMFDefault.File.File                       :\
              Products.Base18.Replica.File18,
    Products.CMFDefault.Image.Image                     :\
              Products.Base18.Replica.Image18,
    Products.CMFDefault.DiscussionItem.DiscussionItem   :\
              Products.Base18.Replica.DiscussionItem18,
    Products.CMFDefault.Favorite.Favorite               :\
              Products.Base18.Replica.Favorite18,
    Products.CMFCore.PortalFolder.PortalFolder          :\
              Products.Base18.Replica.SkinnedFolder18,
    Products.CMFWiki.CMFWikiPage.CMFWikiPage            :\
              Products.Base18.Wiki.CMFWikiPage18,
    Products.CMFWiki.CMFWikiPage.CMFWikiFolder          :\
              Products.Base18.Wiki.CMFWikiFolder18
}

def update_folder(obj):
    """
        Folder needs to be updated in order to take into account
        changes of classes and in particular meta_type
    """
    obase = getattr(obj, 'aq_base', obj)
    new_objects =[]
    if not obase.__dict__.has_key('_objects'):
        return
    for dict in obase.__dict__['_objects']:
        new_objects.append({'id':dict['id'],
                            'meta_type': obj._getOb(dict['id']).meta_type})
    obase.__dict__['_objects'] = tuple(new_objects)

def migrate_branches(migrations, branch, migrated, visited):
    base = getattr(branch, 'aq_base', branch)
    if base in visited:
        # Don't visit again!
        return
    visited.append(base)

    try: changed = branch._p_changed
    except: changed = 1
    for id in branch.objectIds():
        obj = branch._getOb(id)
        LOG("Here",0,id)
        obase = getattr(obj, 'aq_base', obj)
        klass = obase.__class__
        if migrations.has_key(klass):
            # Replace this object.
            changed = 1
            try:
                newob = migrations[klass](obase.id)
                newob.id = obase.id # This line activates obase.
            except:
                newob = migrations[klass](id)
                newob.id = id
            keys = obase.__dict__.keys()
            for k in keys:
                if k is not 'id':
                    migrated.append("  %s" % k)
                    setattr(newob,k,obase.__dict__[k])
            #obase = getattr(newob, 'aq_base', obj)
            #obase.__dict__.update(obase.__dict__)
            #newob.portal_type =
            #      migrations[klass].factory_type_information[0].id
            setattr(branch, id, newob)
                #obj.__class__ = migrations[klass]
            migrated.append(obj.absolute_url())
            # Keep on processing if necessary
            obj = branch._getOb(id)
            obase = getattr(obj, 'aq_base', obj)
            if hasattr(obase, 'objectIds') and \
               re.search('Folder',obase.meta_type) is not None:
                # Enter a sub-branch.
                migrate_branches(migrations, obj, migrated, visited)
                # Update meta_type
                update_folder(obj)
        elif hasattr(obase, 'objectIds') and \
                re.search('Folder',obase.meta_type)  is not None:
            # Enter a sub-branch.
            migrate_branches(migrations, obj, migrated, visited)
            # Update meta_type
            update_folder(obj)
        else:
            # Unload this object if it has not been changed.
            try:
                if obj._p_changed is None:
                    obj._p_deactivate()
            except: pass
    if changed is None:
        # Unload this branch.
        object._p_deactivate()
        del visited[-1] # ????

# Main Script
def main(REQUEST):
    container = REQUEST.PARENTS[0]
    pt = container.portal_types
    ps = container.portal_skins
    # Add FTI
    ptlist = ['Document','Image','File','Link','News Item','Folder',
              'Discussion Item','Favorite','Translation','Wiki', 'Wiki Page']
    for oid in ptlist:
        try: pt.manage_delObjects((oid,))
        except: pass
        pt.manage_addTypeInformation(id=oid,typeinfo_name="Base18: Base18 %s"
                                     % oid)
    # Add Skin
    try:
        from Products.CMFCore.DirectoryView import createDirectoryView
        createDirectoryView(ps,'Products/Base18/skins/content18',
                            id='content18')
    except: pass
    # Add Translation and Membership Tools
    try: container.manage_delObjects(('portal_membership',))
    except: pass
    addBase18Tool = container.manage_addProduct['Base18'].manage_addTool
    try: addBase18Tool('Base18 Translation Tool', None)
    except: pass
    try: addBase18Tool('Base18 Membership Tool', None)
    except: pass
    # Eventually keep folder on preferences here
    # Add Message Catalog
    from Products.Localizer.MessageCatalog import manage_addMessageCatalog
    try: manage_addMessageCatalog(container, 'gettext', '',('en',))
    except: pass
    # Update Content
    visited = []
    migrated = []
    migrate_branches(migrations, container, migrated, visited)
    update_folder(container)
    from string import join
    return 'Converted:\n%s\n\nDone.' % join(migrated, '\n')

# Show Attributes
def showDict(self):
    ob = getattr(self,'aq_base')
    return "%s \n %s" % (str(ob.__class__) , ob.__dict__)
    #return str(ob.__class__) + '\n' + str(ob.meta_type) + '\n' +
    #       str(ob.portal_type) + '\n'
