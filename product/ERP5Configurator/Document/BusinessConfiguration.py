##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
#                    Ivan Tyagov <ivan@nexedi.com>
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

import time
from AccessControl import ClassSecurityInfo
from Globals import PersistentMapping
from Acquisition import aq_base
from Products.ERP5Type import Permissions, PropertySheet
from zLOG import LOG, INFO
from cStringIO import StringIO

from Products.ERP5Configurator.Tool.ConfiguratorTool import _validateFormToRequest
from Products.ERP5.Document.Item import Item

## Workflow states definitions
INITIAL_STATE_TITLE = 'Start'
DOWNLOAD_STATE_TITLE = 'Download'
END_STATE_TITLE = 'End'

class BusinessConfiguration(Item):
  """
    BusinessConfiguration store the values enter by the wizard. 
  """

  meta_type = 'ERP5 Business Configuration'
  portal_type = 'Business Configuration'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Item
                    , PropertySheet.Arrow
                    , PropertySheet.BusinessConfiguration
                    , PropertySheet.Comment
                    , PropertySheet.Version
                    )

  security.declareProtected(Permissions.View, 'isInitialConfigurationState')
  def isInitialConfigurationState(self):
    """ Check if the Business Configuration is on initial workflow state
    """
    workflow =  self.getResourceValue()
    if workflow is not None:
      return self.getCurrentState() == workflow.getSource()
    return None

  security.declareProtected(Permissions.View, 'isDownloadConfigurationState')
  def isDownloadConfigurationState(self):
    """ Check if the Business Configuration is on Download State
    """
    return self.getCurrentStateTitle() == DOWNLOAD_STATE_TITLE 

  security.declareProtected(Permissions.View, 'isEndConfigurationState')
  def isEndConfigurationState(self):
    """ Check if the Business Configuration is on End State
    """
    return self.getCurrentStateTitle() == END_STATE_TITLE

  security.declareProtected(Permissions.View, 'getNextTransition')
  def getNextTransition(self):
    """ Return next transition. """
    current_state = self.getCurrentStateValue()
    if current_state is None:
      return None
    transition_list = current_state.getAvailableTransitionList(self)
    transition_number = len(transition_list)
    if transition_number > 1:
      raise TypeError, "More than one transition is available."
    elif transition_number == 0:
      return None
    
    return transition_list[0]

  security.declarePrivate('_executeTransition')
  def _executeTransition(self, \
                        form_kw=None,
                        request_kw=None):
    """ Execute the transition. """
    root_conf_save = None
    if form_kw is None:
      form_kw = {}
    current_state = self.getCurrentStateValue()
    transition = self.getNextTransition()
    next_state = self.unrestrictedTraverse(transition.getDestination())
    ## it's possible that we have already saved a configuration save object 
    ## in workflow_history for this state so we use it
    root_conf_save = self._getConfSaveForStateFromWorkflowHistory()
    if root_conf_save is None:
      ## we haven't saved any configuration save for this state so create new one
      root_conf_save = self.newContent(portal_type='Configuration Save')
    else:
      ## we have already created configuration save for this state
      ## so remove from it already existing configuration items
      if root_conf_save!=self: ## don't delete ourselves
        existing_conf_items = root_conf_save.objectIds()
        existing_conf_items = map(None, existing_conf_items)
        root_conf_save.manage_delObjects(existing_conf_items)
    ## save ...
    root_conf_save.edit(**form_kw)
    ## Add some variables so we can get use them in workflow after scripts
    form_kw['configuration_save_url'] = root_conf_save.getRelativeUrl()
    form_kw['transition'] = transition.getRelativeUrl()
    current_state.executeTransition(transition, self, form_kw=form_kw)

  security.declarePrivate('_displayNextForm')
  def _displayNextForm(self, \
                       validation_errors=None, \
                       context=None, \
                       transition=None):
    """ Render next form. """
    if transition is None:
      transition = self.getNextTransition()
    while transition is not None:
      form_id = transition.getTransitionFormId()
      current_state = self.getCurrentStateValue()
      if self.isDownloadConfigurationState():
        ## exec next transition for this business configuration 
        self._executeTransition()
        transition = self.getNextTransition()
        return None, None, None, None, None
      if form_id is None:
        ## go on until you find a form
        self._executeTransition()
        transition = self.getNextTransition()
      else:
        if context is None:
          ## examine workflow_history for already saved 
          ## 'Configuration Save' objects for this state
          context = self._getConfSaveForStateFromWorkflowHistory()
        ## get form object in a proper context
        form_html, form_title = self._renderFormInContext(form_id, context, validation_errors)
        ## check if we've can shown 'Previous' button
        previous = None
        translate = self.Base_translateString
        if self._isAlreadyConfSaveInWorkflowHistory(transition):
          previous = translate("Previous")
        return previous, form_html, form_title, \
               translate(transition.getTitle()), self.getServerBuffer()

  security.declarePrivate('_renderFormInContext')
  def _renderFormInContext(self, form_id, context, validation_errors):
    html = ""
    html_forms = []
    isMultiEntryTransition = self._isMultiEntryTransition()
    forms_number = isMultiEntryTransition
    if context is None:
      form = getattr(self, form_id)
      if not isMultiEntryTransition:
        if validation_errors is not None:
          self.REQUEST.set('field_errors', form.ErrorFields(validation_errors))
        html = form()
      else:
        template_html = form()
        for form_counter in range(0, forms_number):
          form_html = self.Base_mainConfiguratorFormTemplate(
                                  current_form_number = form_counter + 1, 
                                  max_form_numbers = forms_number,
                                  form_title = form.title,                               
                                  form_html = template_html)
          html_forms.append(form_html)
    else:
      if not isMultiEntryTransition:
        ## only one form saved under this context
        form = getattr(context, form_id)
        if validation_errors is not None:
          self.REQUEST.set('field_errors', form.ErrorFields(validation_errors))
        html = form()
      else:
        ## we have many forms saved under this context
        form = getattr(self, form_id)
        field_ids = form.get_fields()
        for form_counter in range(0, forms_number):
          ## fill REQUEST with data as it will be used to render form
          for field in field_ids:
            field_value = getattr(context, "field_%s" %field.id, None)
            if field_value is not None and len(field_value) > form_counter:
              field_value = field_value[form_counter]
              self.REQUEST.set(field.id, field_value)
            else:
              self.REQUEST.set(field.id, '')
          form_html = self.Base_mainConfiguratorFormTemplate( \
                             current_form_number = form_counter +1, \
                             max_form_numbers = forms_number, \
                             form_html = getattr(context, form_id)())
          html_forms.append(form_html)
    if html_forms!=[]:
      html = "\n".join(html_forms)
    title = form.title  
    return html, title

  security.declarePrivate('_displayPreviousForm')
  def _displayPreviousForm(self):
    """ Render previous form using workflow history. """
    workflow_history = self.getCurrentStateValue().getWorkflowHistory(self, remove_undo=1)
    workflow_history.reverse()   
    for wh in workflow_history:
      ## go one step back
      current_state = self.getCurrentStateValue()
      current_state.undoTransition(self)
      transition = self.unrestrictedTraverse(wh['transition'])
      conf_save = self.unrestrictedTraverse(wh['configuration_save_url'])
      ## check if this transition can be shown to user ...
      if transition._checkPermission(self) and \
           transition.getTransitionFormId() is not None:
        return  self._displayNextForm(context=conf_save, transition=transition)
  
  security.declarePrivate('_validateNextForm')
  def _validateNextForm(self, **kw):
    """ Validate the form displayed to the user. """
    REQUEST = self.REQUEST
    form = getattr(self, self.getNextTransition().getTransitionFormId())
    return _validateFormToRequest(form, REQUEST, **kw)

  #############
  ## misc    ##
  #############
  security.declarePrivate('_getConfigurationStack')
  def _getConfigurationStack(self):
    """ Return list of created by client configuration save objects 
        sort on id which is an integer. """
    result = self.objectValues('ERP5 Configuration Save')
    result = map(None, result)
    result.sort(lambda x, y: cmp(x.getIntIndex(x.getIntId()),
                                 y.getIntIndex(y.getIntId())))
    return result

  security.declarePrivate('_getConfSaveForStateFromWorkflowHistory')
  def _getConfSaveForStateFromWorkflowHistory(self):
    """ Get from workflow history configuration save for this state """
    configuration_save = None
    current_state = self.getCurrentStateValue()
    transition = self.getNextTransition()
    next_state = self.unrestrictedTraverse(transition.getDestination())
    workflow_history = current_state.getWorkflowHistory(self)
    for wh in workflow_history:
      wh_state = self.unrestrictedTraverse(wh['current_state'])
      if wh_state == next_state:
        configuration_save = self.unrestrictedTraverse(wh['configuration_save_url'])
    return configuration_save

  security.declarePrivate('_isAlreadyConfSaveInWorkflowHistory')
  def _isAlreadyConfSaveInWorkflowHistory(self, transition):
    """ check if we have an entry in worklow history for this state """
    workflow_history = self.getCurrentStateValue().getWorkflowHistory(self, remove_undo=1)
    workflow_history.reverse()
    for wh in workflow_history:
      wh_state = self.unrestrictedTraverse(wh['current_state'])
      for wh_transition in wh_state.getAvailableTransitionList(self):
        if wh_transition.getTransitionFormId() is not None and wh_transition!=transition:
          return True
    return False

  security.declarePrivate('_isMultiEntryTransition')
  def _isMultiEntryTransition(self):
    """ Return number of multiple forms to show for a transition. """
    next_transition = self.getNextTransition()
    if next_transition is not None:
      if getattr(aq_base(self), '_multi_entry_transitions', None) is not None:
        multi_forms = self._multi_entry_transitions.get(next_transition.getRelativeUrl(), 0)
        if multi_forms == 1:
          # we have set '1' which means show one form which is not multiple forms
          multi_forms = 0
        return multi_forms
      else:
        return 0
    else:
      ## no transitions available
      return 0

  security.declareProtected(Permissions.ModifyPortalContent, 'setMultiEntryTransition')
  def setMultiEntryTransition(self, transition_url, max_entry_number):
    """ Set a transition as multiple - i.e max_entry_number of forms 
        which will be rendered. This method is called in after scripts
        and usually this number is set by user in a web form. """
    if getattr(aq_base(self), '_multi_entry_transitions', None) is None:
      self._multi_entry_transitions = PersistentMapping()
    self._multi_entry_transitions[transition_url] = max_entry_number

  security.declareProtected(Permissions.ModifyPortalContent, 'setServerBuffer')
  def setServerBuffer(self, **kw):
    """ Set what we should return to client. """
    if getattr(aq_base(self), '_server_buffer', None) is None:
      self._server_buffer = {}
    for item, value in kw.items():
      self._server_buffer[item] = value
    self._p_changed = 1

  security.declareProtected(Permissions.View, 'getServerBuffer')
  def getServerBuffer(self):
    """ Get return buffer which will be sent to client and 
    afterwards deleted. """
    server_buffer = getattr(aq_base(self), '_server_buffer', {})
    self._server_buffer = {}
    return server_buffer

  security.declareProtected(Permissions.ModifyPortalContent, 'setGlobalConfigurationAttr')
  def setGlobalConfigurationAttr(self, **kw):
    """ Set global business configuration attribute. """
    if getattr(aq_base(self),
               '_global_configuration_attributes', None) is None:
      self._global_configuration_attributes = PersistentMapping()
    for key, value in kw.items():
      self._global_configuration_attributes[key] = value

  security.declareProtected(Permissions.View, 'getGlobalConfigurationAttr')
  def getGlobalConfigurationAttr(self, key, default = None):
    """ Get global business configuration attribute. """
    global_configuration_attributes = getattr(self, '_global_configuration_attributes', {})
    return global_configuration_attributes.get(key, default)

  security.declareProtected(Permissions.View, 'getBuiltBusinessConfigurationBT5List')
  def getBuiltBusinessConfigurationBT5List(self):
    """
      Get list of built business templates in a Wizard format.
    """
    bt5_file_list = []
    portal = self.getPortalObject()
    for bt_link in self.contentValues(portal_type="Link"):
      bt5_item = dict(bt5_id = bt_link.getUrlString(), 
                      bt5_filedata = "")
      bt5_file_list.append(bt5_item)

    for bt_file in self.contentValues(portal_type="File"):
      bt5_item = dict(bt5_id = bt_file.getId(),
                      bt5_filedata = bt_file.getData())
      bt5_file_list.append(bt5_item)
    return bt5_file_list

  ############# Instance and Business Configuration ########################
  security.declareProtected(Permissions.ModifyPortalContent, 'buildConfiguration')
  def buildConfiguration(self):
    """ 
      Build list of business templates according to already saved 
      Configuration Saves (i.e. user input).
      This is the actual implementation which can be used from workflow 
      actions and Configurator requets
    """
    bt5_file_list = []
    start = time.time()
    bc_id = self.getId()
    LOG("CONFIGURATOR", INFO, 
        'Build process started for %s' % self.getRelativeUrl())
    conf_item_list = []
    # build
    for conf_save in self._getConfigurationStack():
      # XXX: check which items are configure-able
      conf_item_list = [x for x in conf_save.contentValues()]
      conf_item_list.sort(lambda x,y: cmp(x.getIntId(), y.getIntId()))
      for conf_item in conf_item_list:
        conf_save_id = conf_save.getId()
        configuration_item_object = conf_item
        LOG('CONFIGURATOR', INFO, 'Building --> %s' % conf_item)
        start_build = time.time()
        build_result = conf_item.build(self)
        LOG('CONFIGURATOR', INFO, 'Built    --> %s (%.02fs)' \
                          % (conf_item, time.time()-start_build))
       
    # save list of generated or reused bt5 ids in bc
    LOG('CONFIGURATOR', INFO, 
        'Build process started for %s ended after %.02fs' 
          %(self.getRelativeUrl(), time.time()-start))
    return bt5_file_list

  security.declareProtected(Permissions.ModifyPortalContent, 'resetBusinessConfiguration')
  def resetBusinessConfiguration(self):
    """ 
      Reset Business Confiration at server side.
      Remove all traces from user input (i.e. Configuration Saves, workflow history).
    """
    object_ids = []
    for obj in self.contentValues(filter = {'portal_type': ['Configuration Save', 'File', 'Link']}):
      object_ids.append(obj.getId())
    self.manage_delObjects(object_ids)
    del self.workflow_history
    # ERP5 Workflow initialization
    erp5_workflow = self.getResourceValue()
    erp5_workflow.initializeDocument(self)

  def isStandardBT5(self, bt5_id):
    """Is bt5_id standard gzipped bt5 id?
       Use ERP5 site portal_templates to get list of bt5_ids from configured
       repository. This relies on the fact that the host site have a
       configured repository.
    """
    # XXX This should be one API from portal_templates
    bt5_title_list = []
    bt5_title = bt5_id.split('.')[0]
    for bt5 in self.getPortalObject().portal_templates\
        .getRepositoryBusinessTemplateList():
      bt5_title_list.append(bt5.getTitle())
    return bt5_title in bt5_title_list

  def getPublicUrlForBT5Id(self, bt5_id):
    """ Generate publicly accessible URL for business template """
    portal = self.getPortalObject()
    return portal.portal_templates.getBusinessTemplateUrl(None, bt5_id)

  security.declareProtected(Permissions.ModifyPortalContent, 'installConfiguration')
  def installConfiguration(self, execute_after_setup_script = 1):
    """ 
      Install in remote instance already built list of business templates 
      which are saved in the Business Configuration.
    """
    kw = dict(tag="start")
    bt5_file_list = []
    portal = self.getPortalObject()
    for bt_link in self.contentValues(portal_type="Link"):
      portal.portal_templates.activate(**kw).updateBusinessTemplateFromUrl(
                                        bt_link.getUrlString())
      LOG("Business COnfiguration", INFO,
          "Install %s to %s" % (bt_link.getUrlString(), self.getRelativeUrl()))
      kw["after_tag"] = kw["tag"]
      kw["tag"] = bt_link.getTitle()

    for bt_file in self.contentValues(portal_type="File"):
      if bt_file.getTitle("").replace(".bt5", "") == self.getSpecialiseTitle():
        bt5_io = StringIO(str(bt_file.getData()))

        # XXX FIXME (lucas): Why FAIL on the log message? 
        LOG("Business Configuration", INFO, 
            "[FAIL] Import of bt5 file (%s - %s)" % \
                                      (bt_file.getId(), bt_file.getTitle()))

        bc = portal.portal_templates.importFile(import_file=bt5_io,
                                         batch_mode=1)
        bc.activate(**kw).install()
        kw["after_tag"] = kw["tag"]
        kw["tag"] = bt_file.getTitle()

    if execute_after_setup_script:
      customer_template = self.getSpecialiseValue()
      customer_template_relative_url = customer_template.getRelativeUrl()
      self.activate(**kw).ERP5Site_afterConfigurationSetup(
                customer_template_relative_url=customer_template_relative_url,
                alter_preferences=True)
      LOG("Business Configuration", INFO,
          "After setup script called (force) for %s : %s" %
                    (self.getRelativeUrl(), self.getSpecialise()))

