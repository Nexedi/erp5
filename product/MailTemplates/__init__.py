from __future__ import absolute_import
# Copyright (c) 2005-2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from AccessControl import allow_module,allow_class
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from .MailTemplate import MailTemplate
from six.moves.urllib.parse import quote

try:
    import Products.CMFCore
except ImportError:
    pass
else:
    from . import FSMailTemplate
    import Products.CMFCore.utils
    Products.CMFCore.utils.registerIcon(FSMailTemplate.FSMailTemplate,
                                        'www/fsmt.gif', globals())

def initialize( context ):
    context.registerClass(
        MailTemplate,
        # we use the same permission as page templates
        # in order to keep things simple.
        permission='Add Page Templates',
        constructors=(addMailTemplateForm,
                      addMailTemplate),
        icon='www/mt.gif',
        )

addMailTemplateForm = PageTemplateFile(
    'www/mtAdd',
    globals(),
    __name__='addMailTemplateForm'
    )
def addMailTemplate(self, id, mailhost=None, text=None,
                           REQUEST=None, submit=None):
    "Add a Mail Template with optional file content."

    id = str(id)
    if REQUEST is None:
        self._setObject(id, MailTemplate(id, text))
        ob = getattr(self, id)
        if mailhost:
            ob._setPropValue('mailhost',mailhost)
        return ob
    else:
        file = REQUEST.form.get('file')
        headers = getattr(file, 'headers', None)
        if headers is None or not file.filename:
            mt = MailTemplate(id, text)
        else:
            mt = MailTemplate(id, file, headers.get('content_type'))

        self._setObject(id, mt)
        ob = getattr(self, id)
        if mailhost:
            ob._setPropValue('mailhost',mailhost)


        if submit == " Add and Edit ":
            u = ob.absolute_url()
        else:
            u = ob.aq_parent.absolute_url()
        REQUEST.RESPONSE.redirect(u+'/manage_main')

# allow all the email module's public bits
import email
import inspect
for name in email.__all__:
    path = 'email.'+name
    allow_module(path)
    try:
        mod = __import__(path)
    except ImportError:
        pass
    else:
        mod = getattr(mod,name)
        for mod_name in dir(mod):
            obj = getattr(mod,mod_name)
            if inspect.isclass(obj):
              allow_class(obj)
