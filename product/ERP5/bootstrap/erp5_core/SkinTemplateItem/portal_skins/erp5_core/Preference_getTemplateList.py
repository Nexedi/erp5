'''Returns the list of templates contained in this preferences.

This is a specific case, because template document are not catalogued, and if
this listbox were using contentValues as list method the the view mode to list
mode proxy would use searchFolder in this case (see
ERP5Form/Extensions/ListBox_getListModeProxyListMethodName.py for the detail),
and searchFolder won't returns any document, as they are not in catalog.
'''
return context.contentValues(**kw)
