# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Pierre Ducroquet <pierre.ducroquet@nexedi.com>
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

from __future__ import absolute_import
from Products.Formulator import Widget, Validator
from Products.Formulator.Field import ZMIField
from Products.Formulator.DummyField import fields
from Products.Formulator.Errors import ValidationError
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import DTMLFile
from Products.ERP5Type.Utils import str2bytes
from Products.Formulator.TALESField import TALESField
from . import CaptchasDotNet
import string
import random
from hashlib import md5
import time
from zope.interface import Interface
from zope.interface import implementer

class ICaptchaProvider(Interface):
  """The CaptchaProvider interface provides a captcha generator."""

  def generate(self, field):
    """Returns a tuple (key, valid_answer) for this captcha.
    That key is never sent directly to the client, it is always hashed before."""

  def getHTML(self, field, captcha_key):
    """Returns the HTML code for the given captcha key"""

  def getExtraPropertyList(self):
    """Returns the list of additionnary properties that are configurable"""

@implementer(ICaptchaProvider)
class CaptchasDotNetProvider(object):

  def getImageGenerator (self, field):
    captchas_client = field.get_value("captcha_dot_net_client") or "demo"
    captchas_secret = field.get_value("captcha_dot_net_secret") or "secret"
    captchas_use_ssl = field.get_value("captcha_dot_net_use_ssl") or False
    return CaptchasDotNet.CaptchasDotNet(client = captchas_client,
                                        secret = captchas_secret,
                                        use_ssl = captchas_use_ssl)

  def generate(self, field):
    image_generator = self.getImageGenerator(field)
    captcha_key = image_generator.random_string()
    return (captcha_key, image_generator.get_answer(captcha_key))

  def getHTML(self, field, captcha_key):
    image_generator = self.getImageGenerator(field)
    return image_generator.image(captcha_key, "__captcha_" + md5(str2bytes(captcha_key)).hexdigest())

  # dynamic fields
  _dynamic_property_list = [dict(id='captcha_dot_net_client',
                                 title='Captchas.net client login',
                                 description='Your login on captchas.net to get the pictures.',
                                 default="demo",
                                 size=32,
                                 required=0),
                            dict(id='captcha_dot_net_secret',
                                 title='Captchas.net client secret',
                                 description='Your secret on captchas.net to get the pictures.',
                                 default="secret",
                                 size=32,
                                 required=0),
                            dict(id='captcha_dot_net_use_ssl',
                                 title='Captchas.net ssl connection',
                                 description='Use secured connection with the service',
                                 default=0,
                                 required=0)]

  def getExtraPropertyList(self):
    return [fields.StringField(**self._dynamic_property_list[0]),
            fields.PasswordField(**self._dynamic_property_list[1]),
            fields.CheckBoxField(**self._dynamic_property_list[2])]

  def getExtraTalesPropertyList(self):
    return [TALESField(**self._dynamic_property_list[0]),
            TALESField(**self._dynamic_property_list[1]),
            TALESField(**self._dynamic_property_list[2])]

@implementer(ICaptchaProvider)
class NumericCaptchaProvider(object):

  # No division because it would create decimal numbers
  operator_set = {"+": "plus", "-": "minus", "*": "times"}

  def generate(self, field):
    # First step : generate the calculus. It is really simple.
    terms = [str(random.randint(1, 20)), random.choice(list(self.operator_set.keys()))]
    #XXX: Find a way to prevent too complex captchas (for instance 11*7*19...)
    #terms += [str(random.randint(1, 20)), random.choice(operator_set.keys())]
    terms.append(str(random.randint(1, 20)))

    # Second step : generate a text for it, and compute it
    calculus_text = " ".join(terms)
    result = eval(calculus_text)

    return (calculus_text, str(result))

  def getHTML(self, field, captcha_key):
    # Make the text harder to parse for a computer
    calculus_text = captcha_key
    for (operator, replacement) in self.operator_set.items():
      calculus_text = calculus_text.replace(operator, replacement)

    return "<span class=\"%s\">%s</span>" % (field.get_value('css_class'), calculus_text)

  def getExtraPropertyList(self):
    return []

  def getExtraTalesPropertyList(self):
    return []

class CaptchaProviderFactory(object):
  @staticmethod
  def getProvider(name):
    if name == "numeric":
      return NumericCaptchaProvider()
    elif name == "text":
      return CaptchasDotNetProvider()
    return None

  @staticmethod
  def getProviderList():
    return [('Mathematics', 'numeric'), ('Text recognition (using captchas.net)', 'text')]

  @staticmethod
  def getDefaultProvider():
    return "numeric"

class CaptchaWidget(Widget.TextWidget):
  """
    A widget that displays a Captcha.
  """

  def add_captcha(self, portal_sessions, key, value):
    session = portal_sessions[key]
    if key in session:
      return False
    session[key] = value
    return True

  def validate_answer(self, portal_sessions, key, value):
    session = portal_sessions[key]
    if not(key in session):
      return False
    result = (session[key] == value)
    # Forbid several use of the same captcha.
    del(session[key])
    return result

  property_names = Widget.Widget.property_names + ['captcha_type']

  captcha_type = fields.ListField('captcha_type',
                                   title='Captcha type',
                                   description=("The type of captcha you want to use."),
                                   default=CaptchaProviderFactory.getDefaultProvider(),
                                   required=1,
                                   size=1,
                                   items=CaptchaProviderFactory.getProviderList())

  def render(self, field, key, value, REQUEST, render_prefix=None):
    """
      Render editor
    """
    captcha_key = None
    captcha_field = None
    captcha_type = field.get_value("captcha_type")
    provider = CaptchaProviderFactory.getProvider(captcha_type)
    (captcha_key, captcha_answer) = provider.generate(field)
    portal_sessions = field.getPortalObject().portal_sessions
    retries = 10
    while retries:
      if self.add_captcha(portal_sessions, md5(str2bytes(captcha_key)).hexdigest(), captcha_answer):
        (captcha_key, captcha_answer) = provider.generate(field)
        break
      retries = retries - 1
    else:
      raise RuntimeError("Error adding captcha")

    captcha_field = provider.getHTML(field, captcha_key)

    key_field = Widget.render_element("input",
                                      type="hidden",
                                      name="__captcha_" + key + "__",
                                      value=md5(str2bytes(captcha_key)).hexdigest())
    splitter = "<br />"
    answer = Widget.render_element("input",
                                   type="text",
                                   name=key,
                                   css_class=field.get_value('css_class'),
                                   size=10)
    # HTML page having a captcha field should never be cached.
    REQUEST.RESPONSE.setHeader('Cache-Control', 'max-age=0, no-store')
    return captcha_field + key_field + splitter + answer

  def render_view(self, field, value, REQUEST=None, render_prefix=None):
    """
      Render form in view only mode.
    """
    return None

CaptchaWidgetInstance = CaptchaWidget()

class CaptchaValidator(Validator.Validator):
  message_names = Validator.Validator.message_names + ['wrong_captcha']

  wrong_captcha = 'You did not enter the right answer.'

  def validate(self, field, key, REQUEST):
    value = REQUEST.get(key, None)
    cache_key = REQUEST.get("__captcha_" + key + "__")
    portal_sessions = field.getPortalObject().portal_sessions
    if not(CaptchaWidgetInstance.validate_answer(portal_sessions, cache_key, value)):
      self.raise_error('wrong_captcha', field)
    return value

CaptchaValidatorInstance = CaptchaValidator()

class CaptchaField(ZMIField):
  security = ClassSecurityInfo()
  meta_type = "CaptchaField"

  widget = CaptchaWidgetInstance
  validator = CaptchaValidatorInstance

  # methods screen
  security.declareProtected('View management screens',
                            'manage_main')
  manage_main = DTMLFile('dtml/captchaFieldEdit', globals())

  security.declareProtected('Change Formulator Forms', 'manage_edit')
  def manage_edit(self, REQUEST):
    """
    Surcharged values for the captcha provider custom fields.
    """
    captcha_provider = CaptchaProviderFactory.getProvider(self.get_value("captcha_type"))
    result = {}
    for field in captcha_provider.getExtraPropertyList():
      try:
        # validate the form and get results
        result[field.get_real_field().id] = field.get_real_field().validate(REQUEST)
      except ValidationError as err:
        if REQUEST:
          message = "Error: %s - %s" % (err.field.get_value('title'),
                                        err.error_text)
          return self.manage_main(self, REQUEST,
                                  manage_tabs_message=message)
        else:
          raise

    # Edit standards attributes
    # XXX It is not possible to call ZMIField.manage_edit because
    # it returns at the end...
    # we need to had a parameter to the method
    try:
      # validate the form and get results
      result.update(self.form.validate(REQUEST))
    except ValidationError as err:
      if REQUEST:
        message = "Error: %s - %s" % (err.field.get_value('title'),
                                      err.error_text)
        return self.manage_main(self,REQUEST,
                                manage_tabs_message=message)
      else:
        raise

    self.values.update(result)

    # finally notify field of all changed values if necessary
    for key in result:
      method_name = "on_value_%s_changed" % key
      if hasattr(self, method_name):
        getattr(self, method_name)(result[key])

    if REQUEST:
      message="Content changed."
      return self.manage_main(self, REQUEST,
                              manage_tabs_message=message)

  security.declareProtected('Access contents information', 'get_value')
  def get_value(self, id, **kw):
    if id in self.getCaptchaCustomPropertyList():
      return self.values[id]
    return ZMIField.get_value(self, id, **kw)

  def getCaptchaCustomPropertyList(self):
    captcha_type = ZMIField.get_value(self, "captcha_type")
    captcha_provider = CaptchaProviderFactory.getProvider(captcha_type)
    extraPropertyList = captcha_provider.getExtraPropertyList()
    return extraPropertyList



  security.declareProtected('View management screens', 'manage_talesForm')
  manage_talesForm = DTMLFile('dtml/captchaFieldTales', globals())

  security.declareProtected('Change Formulator Forms', 'manage_tales')
  def manage_tales(self, REQUEST):
    """Change TALES expressions.
    """
    result = {}
    # add dynamic form fields for captcha
    #captcha_provider = CaptchaProviderFactory.getProvider(self.get_value("captcha_type"))
    for field in self.getCaptchaCustomTalesPropertyList():
      try:
        # validate the form and get results
        result[field.id] = field.validate(REQUEST)
      except ValidationError as err:
        if REQUEST:
          message = "Error: %s - %s" % (err.field.get_value('title'),
                                        err.error_text)
          return self.manage_talesForm(self, REQUEST,
                                  manage_tabs_message=message)
        else:
          raise

    # standard tales form fields
    try:
      # validate the form and get results
      result.update(self.tales_form.validate(REQUEST))
    except ValidationError as err:
      if REQUEST:
        message = "Error: %s - %s" % (err.field.get_value('title'),
                                      err.error_text)
        return self.manage_talesForm(self,REQUEST,
                                     manage_tabs_message=message)
      else:
        raise
    self._edit_tales(result)

    if REQUEST:
      message="Content changed."
      return self.manage_talesForm(self, REQUEST,
                                   manage_tabs_message=message)

  def getCaptchaCustomTalesPropertyList(self):
    captcha_type = ZMIField.get_value(self, "captcha_type")
    captcha_provider = CaptchaProviderFactory.getProvider(captcha_type)
    extraPropertyList = captcha_provider.getExtraTalesPropertyList()
    return extraPropertyList

