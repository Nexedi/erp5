# Copyright (c) 2005-2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import os

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from App.class_init import default__class_init__ as InitializeClass
from App.Common import package_home
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplate import PageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from BaseMailTemplate import BaseMailTemplate

class MailTemplate(BaseMailTemplate,ZopePageTemplate):
    "A ZPT-like template for sending mails"

    security = ClassSecurityInfo()

    meta_type = 'Mail Template'

    _properties = ()

    manage_options = ZopePageTemplate.manage_options[0:1] + \
                     ZopePageTemplate.manage_options[2:]

    _default_content_fn = os.path.join(package_home(globals()),
                                       'www', 'default.txt')

    security.declareProtected('View management screens','pt_editForm')
    pt_editForm = PageTemplateFile('www/mtEdit', globals(),
                                   __name__='pt_editForm')
    manage = manage_main = pt_editForm

    security.declareProtected('Change Page Templates','pt_editAction')
    def pt_editAction(self, REQUEST, mailhost, text, content_type, expand):
        """Change the mailhost and document."""
        if self.wl_isLocked():
            from webdav.Lockable import ResourceLockedError
            raise ResourceLockedError, "File is locked via WebDAV"
        self.expand=expand
        self._setPropValue('mailhost',mailhost)
        self.pt_edit(text, content_type)
        REQUEST.set('text', self.read()) # May not equal 'text'!
        message = "Saved changes."
        if getattr(self, '_v_warnings', None):
            message = ("<strong>Warning:</strong> <i>%s</i>"
                       % '<br>'.join(self._v_warnings))
        return self.pt_editForm(manage_tabs_message=message)

    def om_icons(self):
        """Return a list of icon URLs to be displayed by an ObjectManager"""
        icons = ({'path': 'misc_/MailTemplates/mt.gif',
                  'alt': self.meta_type, 'title': self.meta_type},)
        if not self._v_cooked:
            self._cook()
        if self._v_errors:
            icons = icons + ({'path': 'misc_/PageTemplates/exclamation.gif',
                              'alt': 'Error',
                              'title': 'This template has an error'},)
        return icons

    def _exec(self, bound_names, args, kw):
        """Call a Page Template"""
        if not kw.has_key('args'):
            kw['args'] = args
        bound_names['options'] = kw

        security=getSecurityManager()
        bound_names['user'] = security.getUser().getIdOrUserName()

        # Retrieve the value from the cache.
        keyset = None
        if self.ZCacheable_isCachingEnabled():
            # Prepare a cache key.
            keyset = {'here': self._getContext(),
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

    def pt_render(self, source=False, extra_context={}):
        # Override to support empty strings
        result = PageTemplate.pt_render(self, source, extra_context) or u''
        assert isinstance(result, unicode)
        return result

InitializeClass(MailTemplate)


