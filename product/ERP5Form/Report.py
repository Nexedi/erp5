##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Globals import InitializeClass, PersistentMapping, DTMLFile
from AccessControl import Unauthorized, getSecurityManager, ClassSecurityInfo
from Products.PythonScripts.Utility import allow_class
from Products.Formulator.DummyField import fields
from Products.Formulator.Form import Form, BasicForm, ZMIForm

from Products.ERP5Type import PropertySheet

from Form import ERP5Form
from Form import create_settings_form as Form_create_settings_form

def create_settings_form():
    form = Form_create_settings_form()
    report_method = fields.StringField(
                         'report_method',
                         title='Report Method',
                         description=('The method to get a list of items (object, form, parameters) '
                                      'to aggregate in a single Report'),
                         default='',
                         required=0)

    form.add_fields([report_method])
    return form

manage_addReport = DTMLFile("dtml/report_add", globals())

def addERP5Report(self, id, title="", REQUEST=None):
    """Add form to folder.
    id     -- the id of the new form to add
    title  -- the title of the form to add
    Result -- empty string
    """
    # add actual object
    id = self._setObject(id, ERP5Report(id, title))
    # respond to the add_and_edit button if necessary
    add_and_edit(self, id, REQUEST)
    return ''    
    
class ERP5Report(ERP5Form):
    """
        An ERP5Form which allows to aggregate a list of 
        forms each of which is rendered on an object with parameters.
        
        Application: create an accounting book from ERP5 objects
        
        - Display the total of each account (report)
        
        - List all accounts
        
        - Display the transactions of each account (one form with listbox)
        
        - List all clients
        
        - Display the transactions of each client (one form with listbox)
        
        - List all vendors
        
        - Display the transactions of each vendor (one form with listbox)
        
    """
    meta_type = "ERP5 Report"
    icon = "www/Form.png"

    # Declarative Security
    security = ClassSecurityInfo()

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem)

    # Constructors
    constructors =   (manage_addReport, addERP5Report)

    # This is a patched dtml formOrder
    security.declareProtected('View management screens', 'formOrder')
    formOrder = DTMLFile('dtml/formOrder', globals())

    # Default Attributes
    report_method = None
    
    # Special Settings
    settings_form = create_settings_form()

    def __init__(self, id, title, unicode_mode=0, encoding='UTF-8', stored_encoding='UTF-8'):
        """Initialize form.
        id    -- id of form
        title -- the title of the form
        """
        ZMIForm.inheritedAttribute('__init__')(self, "", "POST", "", id,
                                               encoding, stored_encoding,
                                               unicode_mode)
        self.id = id
        self.title = title
        self.row_length = 4

    # Proxy method to PageTemplate
    def __call__(self, *args, **kwargs):
        self._v_relation_field_index = 0 # We initialize here an index which is used to generate different method ids for every field
        if not kwargs.has_key('args'):
            kwargs['args'] = args
        form = self
        object = getattr(form, 'aq_parent', None)
        if object:
          container = object.aq_inner.aq_parent
        else:
          container = None
        pt = getattr(self,self.pt)
        report_method = getattr(self,self.report_method)
        extra_context = self.pt_getContext()
        extra_context['options'] = kwargs
        extra_context['form'] = self
        extra_context['container'] = container ## PROBLEM NOT TAKEN INTO ACCOUNT
        extra_context['here'] = object
        extra_context['report_method'] = report_method
        return pt.pt_render(extra_context=extra_context)

    def _exec(self, bound_names, args, kw):
        pt = getattr(self,self.pt)
        return pt._exec(self, bound_names, args, kw)

def add_and_edit(self, id, REQUEST):
    """Helper method to point to the object's management screen if
    'Add and Edit' button is pressed.
    id -- id of the object we just added
    """
    if REQUEST is None:
        return
    try:
        u = self.DestinationURL()
    except:
        u = REQUEST['URL1']
    if REQUEST['submit'] == " Add and Edit ":
        u = "%s/%s" % (u, quote(id))
    REQUEST.RESPONSE.redirect(u+'/manage_main')

def manage_add_report(self, id, title="", unicode_mode=0, REQUEST=None):
    """Add form to folder.
    id     -- the id of the new form to add
    title  -- the title of the form to add
    Result -- empty string
    """
    # add actual object
    id = self._setObject(id, ZMIForm(id, title, unicode_mode))
    # respond to the add_and_edit button if necessary
    add_and_edit(self, id, REQUEST)
    return ''

class ReportSection:
  meta_type = "ReportSection"
  security = ClassSecurityInfo()
  #security.declareObjectPublic()
  
  param_dict = {}

  def __init__(self, path='', form_id='view', param_dict=None ):
    """
      Initialize the line and set the default values
      Selected columns must be defined in parameter of listbox.render...
    """
    
    self.path = path
    self.form_id = form_id
    if param_dict is not None: self.param_dict = param_dict
    
  #security.declarePublic('__getitem__')
  #def __getitem__(self, column_id):
  #  return self.__dict__[column_id]

  security.declarePublic('getTitle')
  def getTitle(self):
    return self.title

  security.declarePublic('getPath')
  def getPath(self):
    return self.path

  security.declarePublic('getObject')
  def getObject(self, context):
    return context.restrictedTraverse(self.path)

  security.declarePublic('getFormId')
  def getFormId(self):
    return self.form_id
  
  security.declarePublic('getParamDict')
  def getParamDict(self):
    return self.param_dict
  
InitializeClass(ReportSection)
allow_class(ReportSection)
