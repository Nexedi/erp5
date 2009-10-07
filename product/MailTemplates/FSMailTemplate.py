# Copyright (c) 2005-2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from App.class_init import default__class_init__ as InitializeClass
from Products.CMFCore.FSPageTemplate import FSPageTemplate,expandpath
from Products.CMFCore.DirectoryView import registerFileExtension
from Products.CMFCore.DirectoryView import registerMetaType

from BaseMailTemplate import BaseMailTemplate
from MailTemplate import MailTemplate

class FSMailTemplate(BaseMailTemplate,FSPageTemplate):
    "Wrapper for Mail Template"
    
    security = ClassSecurityInfo()

    meta_type = 'Filesystem Mail Template'

    def __init__(self, id, filepath, fullname=None, properties=None):
        FSPageTemplate.__init__(self,id,filepath,fullname,properties)
        self._properties = properties

    security.declarePrivate('_createZODBClone')
    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        obj = MailTemplate(self.getId(), self._text, self.content_type)
        obj.expand = 0
        obj.write(self.read())
        obj._setPropValue('mailhost',self.mailhost)
        obj.content_type = self.content_type
        if self._properties:
            keys = self._properties.keys()
            keys.sort()
            for id in keys:
                if id not in ('mailhost','content_type'):
                    obj.manage_addProperty(id,self._properties[id],'string')
        return obj

    security.declarePrivate('_readFile')
    def _readFile(self, reparse):
        fp = expandpath(self._filepath)
        file = open(fp, 'r')    # not 'rb', as this is a text file!
        try:
            data = file.read()
        finally:
            file.close()
        if reparse:
            self.write(data)

    def _exec(self, bound_names, args, kw):
        """Call a FSPageTemplate"""
        try:
            response = self.REQUEST.RESPONSE
        except AttributeError:
            response = None
        # Read file first to get a correct content_type default value.
        self._updateFromFS()

        if not kw.has_key('args'):
            kw['args'] = args
        bound_names['options'] = kw

        security=getSecurityManager()
        bound_names['user'] = security.getUser()

        # Retrieve the value from the cache.
        keyset = None
        if self.ZCacheable_isCachingEnabled():
            # Prepare a cache key.
            keyset = {
                      # Why oh why?
                      # All this code is cut and paste
                      # here to make sure that we
                      # dont call _getContext and hence can't cache
                      # Annoying huh?
                      'here': self.aq_parent.getPhysicalPath(),
                      'bound_names': bound_names}
            result = self.ZCacheable_get(keywords=keyset)
            if result is not None:
                # Got a cached value.
                return result

        # Execute the template in a new security context.
        security.addContext(self)
        try:
            result = self.pt_render(extra_context=bound_names)
            if keyset is not None:
                # Store the result in the cache.
                self.ZCacheable_set(result, keywords=keyset)
            return result
        finally:
            security.removeContext(self)

        return result

InitializeClass(FSMailTemplate)

registerFileExtension('mt', FSMailTemplate)
registerMetaType('Mail Template', FSMailTemplate)
