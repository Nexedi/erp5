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

from AccessControl import ClassSecurityInfo
from Persistence import PersistentMapping
from Acquisition import aq_base
from Products.ERP5Type import Permissions, PropertySheet

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
                    )

  security.declareProtected(Permissions.View, 'isInitialConfigurationState')
  def isInitialConfigurationState(self):
    """ Check if the Business Configuration is on initial workflow state
    """
    workflow = self.getResourceValue()
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

  security.declareProtected(Permissions.ModifyPortalContent, \
      'initializeWorkflow')
  def initializeWorkflow(self):
    """ Initialize Related Workflow"""
    workflow = self.getResourceValue()
    workflow_history = getattr(self, 'workflow_history', {})
    if workflow is None:
      return

    if self.getResource() not in workflow_history:
      if len(self.objectValues("ERP5 Configuration Save")) > 0:
        raise ValueError("Business Configuration Cannot be initialized, \
                          it contains one or more Configurator Save")
      workflow.initializeDocument(self)

  security.declareProtected(Permissions.View, 'getNextTransition')
  def getNextTransition(self):
    """ Return next transition. """
    current_state = self.getCurrentStateValue()
    if current_state is None:
      return None
    transition_list = current_state.getAvailableTransitionList(self)
    transition_number = len(transition_list)
    if transition_number > 1:
      raise TypeError("More than one transition is available.")
    elif transition_number == 0:
      return None

    return transition_list[0]

  security.declarePrivate('_executeTransition')
  def _executeTransition(self, \
                        form_kw=None,
                        request_kw=None):
    """ Execute the transition. """
    if form_kw is None:
      form_kw = {}
    current_state = self.getCurrentStateValue()
    transition = self.getNextTransition()
    ## it's possible that we have already saved a configuration save object
    ## in workflow_history for this state so we use it
    configuration_save = self._getConfSaveForStateFromWorkflowHistory()
    if configuration_save is None:
      ## we haven't saved any configuration save for this state so create new one
      configuration_save = self.newContent(portal_type='Configuration Save',
                                           title=current_state.getTitle())
    else:
      ## we have already created configuration save for this state
      ## so remove from it already existing configuration items
      if configuration_save != self:  # don't delete ourselves
        existing_conf_items = configuration_save.objectIds()
        existing_conf_items = map(None, existing_conf_items)
        configuration_save.manage_delObjects(existing_conf_items)

    modified_form_kw = {}
    for k in form_kw.keys():
      if form_kw[k].__class__.__name__ != 'FileUpload':
        modified_form_kw[k] = form_kw[k]
    configuration_save.edit(**modified_form_kw)
    ## Add some variables so we can get use them in workflow after scripts
    form_kw['configuration_save_url'] = configuration_save.getRelativeUrl()
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
      if self.isDownloadConfigurationState():
        ## exec next transition for this business configuration
        self._executeTransition()
        transition = self.getNextTransition()
        return None, None, None, None
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
               translate(transition.getTitle())

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
                                  current_form_number=form_counter + 1,
                                  max_form_numbers=forms_number,
                                  form_title=form.title,
                                  form_html=template_html)
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
            field_value = getattr(context, "field_%s" % field.id, None)
            if field_value is not None and len(field_value) > form_counter:
              field_value = field_value[form_counter]
              self.REQUEST.set(field.id, field_value)
            else:
              self.REQUEST.set(field.id, '')
          form_html = self.Base_mainConfiguratorFormTemplate( \
                             current_form_number=form_counter + 1,\
                             max_form_numbers=forms_number,\
                             form_html=getattr(context, form_id)())
          html_forms.append(form_html)
    if html_forms != []:
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

  security.declarePrivate('_getConfSaveForStateFromWorkflowHistory')
  def _getConfSaveForStateFromWorkflowHistory(self):
    """ Get from workflow history configuration save for this state """
    configuration_save = None
    current_state = self.getCurrentStateValue()
    transition = self.getNextTransition()
    next_state = self.unrestrictedTraverse(transition.getDestination())
    for wh in current_state.getWorkflowHistory(self):
      if next_state == self.unrestrictedTraverse(wh['current_state']):
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
        if wh_transition.getTransitionFormId() is not None and \
           wh_transition != transition:
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

  security.declareProtected(Permissions.ModifyPortalContent, 'setGlobalConfigurationAttr')
  def setGlobalConfigurationAttr(self, **kw):
    """ Set global business configuration attribute. """
    if getattr(aq_base(self),
               '_global_configuration_attributes', None) is None:
      self._global_configuration_attributes = PersistentMapping()
    for key, value in kw.items():
      self._global_configuration_attributes[key] = value

  security.declareProtected(Permissions.View, 'getGlobalConfigurationAttr')
  def getGlobalConfigurationAttr(self, key, default=None):
    """ Get global business configuration attribute. """
    return getattr(self, '_global_configuration_attributes', {}).get(key, default)

  ############# Instance and Business Configuration ########################
  security.declareProtected(Permissions.ModifyPortalContent, 'buildConfiguration')
  def buildConfiguration(self):
    """
      Build list of business templates according to already saved
      Configuration Saves (i.e. user input).
      This is the actual implementation which can be used from workflow
      actions and Configurator requets
    """
    kw = dict(tag="start_configuration_%s" % self.getId(),
              after_method_id=["updateBusinessTemplateFromUrl",
                               "immediateReindexObject"])
    # build
    configuration_save_list = self.contentValues(portal_type='Configuration Save')
    configuration_save_list.sort(lambda x, y: cmp(x.getIntIndex(x.getIntId()),
                                                  y.getIntIndex(y.getIntId())))
    for configuration_save in configuration_save_list:
      # XXX: check which items are configure-able
      configuration_item_list = configuration_save.contentValues()
      configuration_item_list.sort(lambda x, y: cmp(x.getIntId(), y.getIntId()))
      for configurator_item in configuration_item_list:
        configurator_item.activate(**kw).fixConsistency(
            filter={"constraint_type":"configuration"})
        kw["after_tag"] = kw["tag"]
        kw["tag"] = "configurator_item_%s_%s" % (configurator_item.getId(),
                                                 configurator_item.getUid())

    kw["tag"] = "final_configuration_step_%s" % self.getId()
    kw["after_method_id"] = ["fixConsistency", 'immediateReindexObject']

    self.activate(**kw).ERP5Site_afterConfigurationSetup()

    if self.portal_workflow.isTransitionPossible(self, 'install'):
      self.activate(after_tag=kw["tag"]).install()
