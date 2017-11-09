"""Call the Foo_viewDummyDialog"""
kw.update(context.REQUEST.form)
return context.ERP5Site_redirect("%s/Foo_viewDummyDialog" % context.absolute_url(),
        keep_items={'portal_status_message': '"Update" action is done with "%s".' % string_field}, **kw)
