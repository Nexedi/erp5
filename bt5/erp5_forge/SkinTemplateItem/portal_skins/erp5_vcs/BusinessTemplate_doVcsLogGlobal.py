from erp5.component.module.SubversionClient import SubversionSSLTrustError, SubversionLoginError
from Products.ERP5Type.Document import newTempBase

# get selected business templates
p = context.getPortalObject()
selection_name = 'business_template_selection' # harcoded because we can also get delete_selection
try:
  uid, = p.portal_selections.getSelectionCheckedUidsFor(selection_name)
except ValueError:
  from Products.ERP5.Document.BusinessTemplate import TemplateConditionError
  raise TemplateConditionError('You can select only one Business Template')

business_template = p.portal_catalog.getObject(uid)
return p.REQUEST.RESPONSE.redirect(
  business_template.absolute_url_path() + '/BusinessTemplate_viewVcsLog?added=.')
