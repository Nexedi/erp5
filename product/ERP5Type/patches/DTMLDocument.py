from App.special_dtml import DTMLFile
from OFS.DTMLDocument import DTMLDocument
from Products.ERP5Type import _dtmldir

# Patch for displaying textearea in full window instead of
# remembering a quantity of lines to display in a cookie
manage_editForm = DTMLFile("documentEdit", _dtmldir)
manage_editForm._setName('manage_editForm')
DTMLDocument.manage_editForm = manage_editForm
DTMLDocument.manage = manage_editForm
DTMLDocument.manage_main = manage_editForm
DTMLDocument.manage_editDocument = manage_editForm
DTMLDocument.manage_editForm = manage_editForm
