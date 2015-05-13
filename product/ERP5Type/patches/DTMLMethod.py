from App.special_dtml import DTMLFile
from OFS.DTMLMethod import DTMLMethod
from Products.ERP5Type import _dtmldir

# Patch for displaying textearea in full window instead of
# remembering a quantity of lines to display in a cookie
manage_editForm = DTMLFile("documentEdit", _dtmldir)
manage_editForm._setName('manage_editForm')
DTMLMethod.manage_editForm = manage_editForm
DTMLMethod.manage = manage_editForm
DTMLMethod.manage_main = manage_editForm
DTMLMethod.manage_editDocument = manage_editForm
DTMLMethod.manage_editForm = manage_editForm
