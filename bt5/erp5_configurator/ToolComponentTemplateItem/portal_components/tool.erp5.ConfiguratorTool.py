##############################################################################
#
# Copyright (c) 2006-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
#                    Ivan Tyagov <ivan@nexedi.com>
#                    Rafael Monnerat <rafael@nexedi.com>
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
from Products.ERP5Type.Accessor.Constant import PropertyGetter as \
    ConstantGetter
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.Formulator.Errors import FormValidationError
from DateTime import DateTime

referer = None
installation_status = {'bt5': {'current': 0,
                               'all': 0, },
                       'activity_list': [], }

# cookie name to store user's preferred language name
LANGUAGE_COOKIE_NAME = 'configurator_user_preferred_language'
BUSINESS_CONFIGURATION_COOKIE_NAME = 'business_configuration_key'

def _validateFormToRequest(form, REQUEST, **kw):
  """ Validate form to REQUEST. """
  form_kw = {}
  REQUEST.form = kw
  try:
    form.validate_all_to_request(REQUEST)
    validation_status = 0
    validation_errors = None
  except FormValidationError as e:
    ## not all fields valid
    validation_status = 1
    validation_errors = e
  except Exception as e:
    ## missing fields
    validation_status = 2
    validation_errors = e
  ## extract form arguments and remove leading prefixes
  if validation_status == 0:
    for field in form.get_fields():
      field_id = field.id
      value = getattr(REQUEST, field_id, None)
      for prefix in ('my_', 'your_',):
        if field_id.startswith(prefix):
          attr_id = field_id[len(prefix):]
          form_kw[attr_id] = value
          for del_key in (field.generate_field_key(validation=1), field_id):
            try:
              REQUEST.other.pop(del_key)
            except KeyError:
              pass
  return validation_status, form_kw, validation_errors


class ConfiguratorTool(BaseTool):
  """This tool provides a Configurator Tool.
  """

  id = 'portal_configurator'
  title = 'Configurations'
  meta_type = 'ERP5 Configurator Tool'
  portal_type = 'Configurator Tool'

  isPortalContent = ConstantGetter('isPortalContent', value=True)

  security = ClassSecurityInfo()

  security.declareProtected(Permissions.ManagePortal, 'manage_overview')

  def login(self, REQUEST):
    """ Login client and show next form. """
    bc = REQUEST.get('field_your_business_configuration')
    user_preferred_language = REQUEST.get(
        'field_my_user_preferred_language', None)
    if user_preferred_language:
      # Set language value to request so that next page after login
      # can get the value. Because cookie value is available from
      # next request.
      REQUEST.set(LANGUAGE_COOKIE_NAME, user_preferred_language)
      REQUEST.RESPONSE.setCookie(LANGUAGE_COOKIE_NAME,
                                   user_preferred_language,
                                   path='/',
                                   expires=(DateTime() + 30).rfc822())

    expires = (DateTime() + 1).toZone('GMT').rfc822()
    REQUEST.RESPONSE.setCookie(BUSINESS_CONFIGURATION_COOKIE_NAME,
                               bc,
                               expires=expires)
    REQUEST.set(BUSINESS_CONFIGURATION_COOKIE_NAME, bc)
    return self.next(REQUEST=REQUEST)

  #security.declareProtected(Permissions.ModifyPortalContent, 'next')
  def next(self, REQUEST):
    """ Validate settings and return a new form to the user.  """
    # check if user is allowed to access service
    portal = self.getPortalObject()
    kw = self.REQUEST.form.copy()
    business_configuration = REQUEST.get(BUSINESS_CONFIGURATION_COOKIE_NAME)
    bc = portal.restrictedTraverse(business_configuration)
    if bc is None:
      REQUEST.set('portal_status_message',
                   self.Base_translateString(
                     'You cannot Continue. Unable to find your Business Configuration.'))
      return self.view()
    response = self._next(business_configuration=bc, kw=kw)
    ## Parse server response
    if response["command"] == "show":
      return self.ConfiguratorTool_dialogForm(previous=response['previous'],
                                        form_html=response["data"],
                                        next=response['next'])
    elif response["command"] == "install":
      return self.startInstallation(bc, REQUEST=REQUEST)

  def _next(self, business_configuration, kw):
    """ Return next configuration form and validate previous. """
    form_kw = {}
    need_validation = 1
    validation_errors = None
    response = {}

    business_configuration.initializeWorkflow()

    ## initial state no previous form to validate
    if business_configuration.isInitialConfigurationState():
      need_validation = 0

    ## client can not go further hist business configuration is already built
    if business_configuration.isEndConfigurationState() or \
         business_configuration.getNextTransition() == None:
      return self._terminateConfigurationProcess(response)

    isMultiEntryTransition = business_configuration._isMultiEntryTransition()
    ## validate multiple forms
    if isMultiEntryTransition:
      html_forms = []
      failed_forms_counter = 0
      transition = business_configuration.getNextTransition()
      form = getattr(business_configuration, transition.getTransitionFormId())
      for form_key in [x for x in kw.keys() if x.startswith('field_')]:
        form_kw[form_key] = kw[form_key]
      ## iterate all forms
      for form_counter in range(0, isMultiEntryTransition):
        single_form_kw = {}
        for key, value in form_kw.items():
          if isinstance(value, list) or isinstance(value, tuple):
            ## we have more than one form shown
            single_form_kw[key] = value[form_counter]
            # save original value in request in some cases of multiple forms
            # we need it for validation
            single_form_kw['_original_%s' % key] = value
          else:
            ## even though we have multiple entry transition customer wants
            ## ONE form!
            single_form_kw[key] = value
        ## update properly REQUEST with current form data
        for key, value in single_form_kw.items():
          self.REQUEST.set(key, value)
        ## get validation status
        validation_status, dummy, validation_errors = \
           business_configuration._validateNextForm(**single_form_kw)

        ## clean up REQUEST from traces from validate_all_to_request
        ## otherwise next form will use previous forms details
        cleanup_keys = [x for x in self.REQUEST.other.keys() if x.startswith('my_') or x.startswith('your_')]
        for key in cleanup_keys:
          self.REQUEST.other.pop(key, None)
        ## render HTML code
        if validation_status != 0:
          failed_forms_counter += 1
          ## XXX: form can fail because a new
          ## http://localhost:9080/erp5/portal_wizard/next is issued
          ## without arguments. Improve this
          try:
            self.REQUEST.set('field_errors',
                form.ErrorFields(validation_errors))
          except Exception:
            pass
          single_form_html = form()
          self.REQUEST.other.pop('field_errors', None)
          self.REQUEST.form = {}
        else:
          single_form_html = form()
        ## wrap in form template
        single_form_html = self.Base_mainConfiguratorFormTemplate(
                                current_form_number = form_counter + 1,
                                max_form_numbers = isMultiEntryTransition,
                                form_html = single_form_html)
        ## add to list of forms as html code
        html_forms.append(single_form_html)
      ## return if failure
      if failed_forms_counter > 0:
        next_state = self.restrictedTraverse(business_configuration.getNextTransition()\
            .getDestination())
        html_data = self.Base_mainConfiguratorTemplate(
            form_html = "\n".join(html_forms),
            current_state = next_state,
            business_configuration = business_configuration)
        response.update(command = "show",
                  previous = self.Base_translateString("Previous"),
                  next = self.Base_translateString(transition.getTitle()),
                  data = html_data)
        return response

    ## show next form in transitions
    html = None
    rendered = False
    while rendered is False:
      if need_validation == 1:
        if isMultiEntryTransition:
          ## multiple forms must be validated before
          validation_status = 0
        else:
          validation_status, form_kw, validation_errors = \
              business_configuration._validateNextForm(**kw)
        if validation_status == 1:
          need_validation = 0
        elif validation_status == 2:
          rendered = True
          need_validation = 0
          if business_configuration.getNextTransition() == None:
            ### client can not continue at the momen
            return self._terminateConfigurationProcess(response)
          response["previous"], html, _, response["next"] \
                  = business_configuration._displayNextForm()
        else:
          ## validation passed
          need_validation = 0
          business_configuration._executeTransition(form_kw=form_kw, request_kw=kw)
      elif need_validation == 0:
        if business_configuration.getNextTransition() == None:
          return self._terminateConfigurationProcess(response)
        ## validation failure
        rendered = True
        response["previous"], html, _, response["next"] =\
            business_configuration._displayNextForm(
                validation_errors=validation_errors)

    if html is None:
      ## we have no more forms proceed to build
      response.update(command="install", data=None)
    else:
      ## we have more forms
      next_state = self.restrictedTraverse(business_configuration.getNextTransition()\
          .getDestination())
      html_data = self.Base_mainConfiguratorTemplate(
          form_html = html,
          current_state = next_state,
          business_configuration = business_configuration)
      response.update(command = "show", data = html_data)
    return response

  def _terminateConfigurationProcess(self, response):
    """ Terminate process and return some explanations to client why
        he can no longer continue. """
    response.update(command="show",
                    next=None, \
                    previous=None,
                    data=self.BusinessConfiguration_viewStopForm())
    return response

  #security.declareProtected(Permissions.ModifyPortalContent, 'previous')
  def previous(self, REQUEST):
    """ Display the previous form. """
    # check if user is allowed to access service
    portal = self.getPortalObject()
    kw = self.REQUEST.form.copy()
    business_configuration = REQUEST.get(BUSINESS_CONFIGURATION_COOKIE_NAME)
    bc = portal.restrictedTraverse(business_configuration)
    response = self._previous(business_configuration=bc, kw=kw)
    return self.ConfiguratorTool_dialogForm(previous=response['previous'],
                                      form_html=response['data'],
                                      next=response['next'])

  def _previous(self, business_configuration, kw):
    """ Returns previous form. """
    response = {}
    ## client can not go further his business configuration is already built
    if business_configuration is None or \
         business_configuration.isEndConfigurationState():
      form_html = self.BusinessConfiguration_viewStopForm()
      return self.ConfiguratorTool_dialogForm(form_html = form_html,
                                        next = "Next")

    response['previous'], form_html, _, response['next'] = \
        business_configuration._displayPreviousForm()

    next_state = self.restrictedTraverse(
        business_configuration.getNextTransition().getDestination())

    response['data'] = self.Base_mainConfiguratorTemplate(
        form_html=form_html,
        current_state=next_state,
        business_configuration=business_configuration)
    return response

  security.declarePublic('getInstallationStatusReport')
  def getInstallationStatusReport(self,
                          active_process_id=None, REQUEST=None):
    """ Query local ERP5 instance for installation status.
        If installation is over the installation activities and reindexing
        activities should not exists.
    """
    portal_activities = self.getPortalObject().portal_activities

    if 0 == len(portal_activities.getMessageList()):
      html = self.ConfiguratorTool_viewSuccessfulConfigurationMessageRenderer()
    else:
      # only if bt5s are installed start tracking number of activities
      activity_list = portal_activities.getMessageList()
      installation_status['activity_list'].append(len(activity_list))
      html = self.ConfiguratorTool_viewRunningInstallationMessage(
          installation_status = installation_status)
    # set encoding as this is usually called from asynchronous JavaScript call
    self.REQUEST.RESPONSE.setHeader('Content-Type',
        'text/html; charset=utf-8')
    return html

  security.declareProtected(Permissions.ModifyPortalContent, 'startInstallation')
  def startInstallation(self, business_configuration, REQUEST):
    """ Start installation process as an activity which will
        download/install bt5 template files and meanwhile offer
        user a nice GUI to observe what's happening. """

    # init installation status
    installation_status['bt5']['all'] = 1
    installation_status['bt5']['current'] = 0
    installation_status['activity_list'] = []
    active_process = self.portal_activities.newActiveProcess()
    REQUEST.set('active_process_id', active_process.getId())
    business_configuration.activate(
           active_process=active_process, tag='initialERP5Setup'
        ).build()
    return self.ConfiguratorTool_viewInstallationStatus(REQUEST)
