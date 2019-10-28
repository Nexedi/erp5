"""Hello. This will be long because this godly script does almost everything.

It **always** return a JSON reponse in HATEOAS format specification.

:param REQUEST: HttpRequest holding GET and/or POST data
:param response:
:param view: either "view" or absolute URL of an ERP5 Action
:param mode: {str} help to decide what user wants from us "form" | "search" ...
:param relative_url: an URL of `traversed_document` to operate on (it must have an object_view)
:param portal_status_message: {str} message to be displayed on the user
:param portal_status_level: {str|int} severity of the message using ERP5Type.Log levels or their names like 'info', 'warn', 'error'

Parameters for mode == 'search'
:param query: string-serialized Query
:param select_list: list of strings to select from search result object
:param limit: tuple(start_index, num_records) which is further passed to list_method BUT not every list_method takes it into account
:param form_relative_url: {str} relative URL of a form FIELD issuing the search (listbox/relation field...)
                          it can be None in case of special listboxes like List of Modules
                          or relative path like "portal_skins/erp5_ui_test/FooModule_viewFooList/listbox"
:param default_param_json: {str} BASE64 encoded JSON with parameters intended for the list_method
  :param .form_id: In case of page_template = "form" it will be similar to form_relative_url with the exception that it contains
                   only the form name (e.g. FooModule_viewFooList). In case of dialogs it points to the previous form which is
                   often more important than the dialog form.
:param extra_param_json: {str} BASE64 encoded JSON with parameters for getHateoas script. Content will be put to the REQUEST so
                         it is accessible to all Scripts and TALES expressions.

Parameters for mode == 'form'
:param form: {instace} of a form - obviously this call can be only internal (Script-to-Script)
:param form_data: {dict} cleaned (validated) form data stored in dict where the key is (prefixed) field.id. We do not use it to
                         obtain the value of the field because of how the validation itself work. Take a look in
                         Formulator/Form.validata_all_to_request where REQUEST is modified inplace and in case of first error
                         an exception is thrown which prevents the return thus form_data are empty in case of partial success.
:param extra_param_json: {dict} extra fields to be added to the rendered form

Parameters for mode == 'traverse'
Traverse renders arbitrary View. It can be a Form or a Script.
:param relative_url: string, MANDATORY for obtaining the traversed_document. Calling this script directly on an object should be
                     forbidden in code (but it is not now).
:param view: {str} mandatory. the view reference as defined on a Portal Type (e.g. "view" or "publish_view")
:param extra_param_json: {str} BASE64 encoded JSON with parameters for getHateoas script. Content will be put to the REQUEST so
                         it is accessible to all Scripts and TALES expressions. If view contains embedded **dialog** form then
                         fields will be added to that form to preserve the values for the next step.

# Form
When handling form, we can expect field values to be stored in REQUEST.form in two forms
-  raw string value under key "field_" + <field.id>
-  python-object parsed from raw values under <field.id>
"""

from ZTUtils import make_query
import json
from base64 import urlsafe_b64encode, urlsafe_b64decode
from DateTime import DateTime
from ZODB.POSException import ConflictError
import datetime
import time
from email.Utils import formatdate
import re
from zExceptions import Unauthorized
from Products.ERP5Type.Log import log, DEBUG, INFO, WARNING, ERROR
from Products.ERP5Type.Message import Message
from Products.ERP5Type.Utils import UpperCase
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery
from collections import OrderedDict
from Products.ERP5Form.Selection import Selection

MARKER = []
COUNT_LIMIT = 1000

if REQUEST is None:
  recursive_call = True
  REQUEST = context.REQUEST
else:
  recursive_call = False

if response is None:
  response = REQUEST.RESPONSE


def isFieldType(field, type_name):
  if field.meta_type == 'ProxyField':
    field = field.getRecursiveTemplateField()
  return field.meta_type == type_name


def toBasicTypes(obj):
  """Ensure that  obj contains only basic types."""
  if obj is None:
    return obj
  if isinstance(obj, (bool, int, float, long, str, unicode)):
    return obj
  if isinstance(obj, list):
    return [toBasicTypes(x) for x in obj]
  if isinstance(obj, tuple):
    return tuple(toBasicTypes(x) for x in obj)
  if isinstance(obj, Message):
    return obj.translate()
  try:
    return {toBasicTypes(key): toBasicTypes(obj[key]) for key in obj}
  except:
    log('Cannot convert {!s} to basic types {!s}'.format(type(obj), obj), level=100)
  return obj


def renderHiddenField(form, name, value):
  if form == {}:
    form['_embedded'] = {}
    form['_embedded']['_view'] = {}

  if ('_embedded' in form) and ('_view' in form['_embedded']):
    field_dict = form['_embedded']['_view']
  else:
    field_dict = form

  field_dict[name] = {
    "type": "StringField",  # must be string field because only this gets send when non-editable
    "key": name,
    "default": value,
    "editable": 0,
    "css_class": "",
    "hidden": 1,
    "description": "",
    "title": name,
    "required": 1,
  }


# http://stackoverflow.com/a/13105359
def byteify(string):
  if isinstance(string, dict):
    return {byteify(key): byteify(value) for key, value in string.iteritems()}
  elif isinstance(string, list):
    return [byteify(element) for element in string]
  elif isinstance(string, tuple):
    return tuple(byteify(element) for element in string)
  elif isinstance(string, unicode):
    return string.encode('utf-8')
  else:
    return string


def ensureUTF8(obj):
  """Make sure string is UTF-8, by replacing characters that
  cannot be decoded.
  """
  if isinstance(obj, str):
    return obj.decode('utf-8', 'replace').encode('utf-8')
  elif isinstance(obj, unicode):
    return obj.encode('utf-8', 'replace')
  return obj

def ensureSerializable(obj):
  """Ensure obj and all sub-objects are JSON serializable."""
  if isinstance(obj, dict):
    for key in obj:
      obj[key] = ensureSerializable(obj[key])
  # throw away date's type information and later reconstruct as Zope's DateTime
  elif isinstance(obj, DateTime):
    return obj.ISO() + ' ' + obj.timezone()  # ISO with timezone
  elif isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
    return obj.isoformat()
  # let us believe that iterables don't contain other unserializable objects

  return ensureUTF8(obj)


datetime_iso_re = re.compile(r'^\d{4}-\d{2}-\d{2} |T\d{2}:\d{2}:\d{2}.*$')
time_iso_re = re.compile(r'^(\d{2}):(\d{2}):(\d{2}).*$')
def ensureDeserialized(obj):
  """Deserialize classes serialized by our own `ensureSerializable`.

  Method `byteify` must not be called on the result because it would revert out
  deserialization by calling __str__ on constructed classes.
  """
  if isinstance(obj, dict):
    for key in obj:
      obj[key] = ensureDeserialized(obj[key])
  # seems that default __str__ method is good enough
  if isinstance(obj, str):
    # Zope's DateTime must be good enough for everyone
    if datetime_iso_re.match(obj):
      return DateTime(obj)
    if time_iso_re.match(obj):
      match_obj = time_iso_re.match(obj)
      return datetime.time(*tuple(map(int, match_obj.groups())))
  return obj

NBSP_UTF8 = u'\xA0'.encode('utf-8')
def generateDomainTreeList(url_tool, domain_tool, domain, depth, domain_list):
  if depth:
    domain_list.append((
      '%s%s' % (NBSP_UTF8 * 4 * (depth - 1), domain.getTitle()),
      '/'.join(url_tool.getRelativeContentPath(domain)[2:])
    ))
  new_depth = depth + 1
  for sub_domain in domain_tool.getChildDomainValueList(domain, depth=depth):
    generateDomainTreeList(url_tool, domain_tool, sub_domain, new_depth, domain_list)

def getDomainSelection(domain_list):
  root_dict = {}

  if len(domain_list) > 0:
    category_tool = portal.portal_categories
    domain_tool = portal.portal_domains
    preference_tool = portal.portal_preferences
    url_tool = portal.portal_url

  for base_domain_id in domain_list:
    domain = None
    if category_tool is not None:
      domain = category_tool.restrictedTraverse(base_domain_id, None)
      if domain is not None :

        root_dict[base_domain_id] = getattr(
          domain,
          preference_tool.getPreference(
            'preferred_category_child_item_list_method_id',
            'getCategoryChildCompactLogicalPathItemList'
          )
        )(local_sort_id=('int_index', 'translated_title'), checked_permission='View',
          filter_node=0, display_none_category=0)

      elif domain_tool is not None:
        try:
          domain = domain_tool.getDomainByPath(base_domain_id, None)
        except KeyError:
          domain = None
        if domain is not None:
          # XXX Implement recursive fetch
          domain_list = []
          generateDomainTreeList(url_tool, domain_tool, domain, 0, domain_list)
          root_dict[base_domain_id] = domain_list

  return root_dict


def selectKwargsForCallable(func, initial_kwargs, kwargs_dict):
  """Create a copy of `kwargs_dict` with only items suitable for `func`.

  In case the function cannot state required arguments it throws an AttributeError.
  """
  # TODO: replace `Script_getParams()` with `params()` when https://github.com/zopefoundation/Products.PythonScripts/pull/15 is merged
  script_params = None
  if hasattr(func, 'meta_type'):
    script_params = func.Script_getParams()

  if script_params is not None:
    # In case the func is actualy Script (Python) or ERP5 Python Script
    func_param_list = [tuple(map(lambda x: x.strip(), func_param.split('=')))
                       for func_param in script_params.split(",")
                       if func_param.strip()]
  elif hasattr(func, "func_args"):
    # In case the func is an External Method
    func_param_list = func.func_args
    if len(func_param_list) > 0 and func_param_list[0] == "self":
      func_param_list = func_param_list[1:]
    func_default_list = func.func_defaults
    func_param_list = [(func_param, func_default_list[i]) if len(func_default_list) >= (i + 1) else (func_param, )
                        for i, func_param in enumerate(func_param_list)]

  else:
    # TODO: cover the case of Callables
    # For anything else give up in advance and just return initial guess of the callee
    return initial_kwargs

  # func_param_list is a list of tuples - first item is parameter name and optinal second item is the default value
  func_param_name_list = [item[0] for item in func_param_list]
  for func_param_name in func_param_name_list:
    if '*' in func_param_name:
      continue
    # move necessary parameters from kwargs_dict to initial_kwargs
    if func_param_name not in initial_kwargs and func_param_name in kwargs_dict:
      initial_kwargs[func_param_name] = kwargs_dict.get(func_param_name)
  # MIDDLE-DANGEROUS!
  # In case of reports (later even exports) substitute None for unknown
  # parameters. We suppose Python syntax for parameters!
  # What we do here is literally putting every form field from `kwargs_dict`
  # into search method parameters - this is later put back into `kwargs_dict`
  # this way we can mimic synchronous rendering when all form field values
  # were available in `kwargs_dict`. It is obviously wrong behaviour.
  for func_param in func_param_list:
    if "*" in func_param[0]:
      continue
    if len(func_param) > 1:  # default value exists
      continue
    # now we have only mandatory parameters
    func_param = func_param[0].strip()
    if func_param not in initial_kwargs:
      initial_kwargs[func_param] = None
  # If the method does not specify **kwargs we need to remove unwanted parameters
  if len(func_param_name_list) > 0 and "**" not in func_param_name_list[-1]:
    initial_param_list = tuple(initial_kwargs.keys()) # copy the keys
    for initial_param in initial_param_list:
      if initial_param not in func_param_name_list:
        del initial_kwargs[initial_param]

  return initial_kwargs


url_template_dict = {
  "form_action": "%(traversed_document_url)s/%(action_id)s",
  "traverse_generator": "%(root_url)s/%(script_id)s?mode=traverse" + \
                       "&relative_url=%(relative_url)s&view=%(view)s",
  "traverse_generator_action": "%(root_url)s/%(script_id)s?mode=traverse" + \
                       "&relative_url=%(relative_url)s&view=%(view)s&extra_param_json=%(extra_param_json)s",
  "traverse_template": "%(root_url)s/%(script_id)s?mode=traverse" + \
                       "{&relative_url,view}",

  # Search template will call standard "searchValues" on a document described by `root_url`
  "search_template": "%(root_url)s/%(script_id)s?mode=search" + \
                     "{&query,select_list*,limit*,group_by*,sort_on*,local_roles*,selection_domain*}",
  "worklist_template": "%(root_url)s/%(script_id)s?mode=worklist",
  # Custom search comes with Listboxes where "list_method" is specified. We pass even listbox's
  # own URL so the search can resolve template fields for proper rendering/formatting/editability
  # of the results (because they will be backed up with real documents).
  # :param extra_param_json: contains mainly previous form id to replicate previous search (it is a replacement for Selections)
  "custom_search_template": "%(root_url)s/%(script_id)s?mode=search" + \
                     "&relative_url=%(relative_url)s" \
                     "&form_relative_url=%(form_relative_url)s" \
                     "&list_method=%(list_method)s" \
                     "&extra_param_json=%(extra_param_json)s" \
                     "&default_param_json=%(default_param_json)s" \
                     "{&query,select_list*,limit*,group_by*,sort_on*,local_roles*,selection_domain*}",
  # Non-editable searches suppose the search results will be rendered as-is and no template
  # fields will get involved. Unfortunately, fields need to be resolved because of formatting
  # all the time so we abandoned this no_editable version
  "custom_search_template_no_editable": "%(root_url)s/%(script_id)s?mode=search" + \
                     "&relative_url=%(relative_url)s" \
                     "&list_method=%(list_method)s" \
                     "&default_param_json=%(default_param_json)s" \
                     "{&query,select_list*,limit*,group_by*,sort_on*,local_roles*,selection_domain*}",
  "new_content_action": "%(root_url)s/%(script_id)s?mode=newContent",
  "bulk_action": "%(root_url)s/%(script_id)s?mode=bulk",
  # XXX View is set by default to empty
  "document_hal": "%(root_url)s/%(script_id)s?mode=traverse" + \
                  "&relative_url=%(relative_url)s",
  "jio_get_template": "urn:jio:get:%(relative_url)s",
  "jio_search_template": "urn:jio:allDocs?%(query)s",
  # XXX Hardcoded sub websection
  "login_template": "%(root_url)s/%(login)s",
  "logout_template": "%(root_url)s/%(logout)s"
}

default_document_uri_template = url_template_dict["jio_get_template"]
Base_translateString = context.getPortalObject().Base_translateString


def getRealRelativeUrl(document):
  return '/'.join(portal.portal_url.getRelativeContentPath(document))


def parseActionUrl(url):
  """Parse usual ERP5 Action URL into components: ~root, context~, view_id, param_dict, url.

  :param url: {str} is expected to be in form https://<site_root>/context/view_id?optional=params
  """
  param_dict = {}
  url_and_params = url.split(site_root.absolute_url())[-1].split('?')
  _, script = url_and_params[0].strip("/ ").rsplit('/', 1)
  if len(url_and_params) > 1:
    for param in url_and_params[1].split('&'):
      param_name, param_value = param.split('=')
      if "+" in param_value:
        param_value = param_value.replace("+", " ")
      if ":" in param_name:
        param_name, param_type = param_name.split(":")
        if param_type == "int":
          param_value = int(param_value)
        elif param_type == "bool":
          param_value = True if param_value.lower() in ("true", "1") else False
        else:
          raise ValueError("Cannot convert param {}={} to type {}. Feel free to add implemetation at the position of this exception.".format(
            param_name, param_value, param_type))
      param_dict[param_name] = param_value
  return {
    'view_id': script,
    'params': param_dict,
    'url': url
  }

def getFormRelativeUrl(form):
  return portal.portal_catalog(
    portal_type=("ERP5 Form", "ERP5 Report"),
    uid=form.getUid(),
    id=form.getId(),
    limit=1,
    select_dict={'relative_url': None}
  )[0].relative_url


def getFieldDefault(form, field, key, value=MARKER):
  """Get available value for `field` preferably in python-object from REQUEST or from field's default.

  Previously we used Formulator.Field._get_default which is (for no reason) private.
  """
  value = REQUEST.form.get(field.id, REQUEST.form.get(key, value))
  if value is MARKER:
    # use marker because default value can be intentionally empty string
    value = field.get_value('default', request=REQUEST, REQUEST=REQUEST)
    if field.has_value("unicode") and field.get_value("unicode") and isinstance(value, unicode):
      value = unicode(value, form.get_form_encoding())
  if getattr(value, 'translate', None) is not None:
    return "%s" % value
  return value


def renderField(traversed_document, field, form, value=MARKER, meta_type=None, key=None, key_prefix=None, selection_params=None, request_field=True):
  """Extract important field's attributes into `result` dictionary."""
  if selection_params is None:
    selection_params = {}

  # Some field's TALES expressions suppose field_id to be available in the REQUEST
  # even worse with RelationFields - they render sub-fields (like listbox) but
  # this listbox expects field_id to point to the "parent" relation field
  # thus setting the field_id is optional and controlled by `request_field` argument
  if request_field:
    previous_request_field = REQUEST.other.pop('field_id', None)
    REQUEST.other['field_id'] = field.id

  if meta_type is None:
    meta_type = field.meta_type
  if key is None:
    key = field.generate_field_key(key_prefix=key_prefix)

  if meta_type == "ProxyField":
    # resolve the base meta_type
    meta_type = field.getRecursiveTemplateField().meta_type

  result = {
    "type": meta_type,
    "title": Base_translateString(field.get_value("title")),
    "key": key,
    "css_class": field.get_value("css_class"),
    "editable": field.get_value("editable"),
    "hidden": field.get_value("hidden"),
    "description": field.get_value("description"),
  }

  if "Field" in meta_type:
    # fields have default value and can be required (unlike boxes)
    result["required"] = field.get_value("required") if field.has_value("required") else None
    result["default"] = ensureUTF8(getFieldDefault(form, field, key, value=value))

  # start the actual "switch" on field's meta_type here
  if meta_type in ("ListField", "RadioField", "ParallelListField", "MultiListField"):
    result.update({
      "items": toBasicTypes(field.get_value("items")),
    })
    if meta_type == "ListField":
      result.update({
        "first_item": field.get_value("first_item"),
      })

    if meta_type == "RadioField":
      result.update({
        "select_first_item": field.get_value("first_item"),
        "orientation": field.get_value("orientation"),
      })
    if meta_type in ("ParallelListField", "MultiListField"):
      result.update({
        "sub_select_key": traversed_document.Field_getSubFieldKeyDict(field, 'default:list', key=result["key"]),
        "sub_input_key": "default_" + traversed_document.Field_getSubFieldKeyDict(field, 'default:list:int', key=result["key"])
      })
    return result

  if meta_type in ("StringField", "FloatField", "EmailField", "TextAreaField",
                   "LinesField", "ImageField", "FileField", "IntegerField",
                   "PasswordField", "EditorField"):
    if meta_type == "FloatField":
      result.update({
        "precision": field.get_value("precision"),
        "input_style": field.get_value("input_style"),
      })
    if meta_type == "ImageField":
      options = {
        'display': field.get_value('image_display'),
        'format': field.get_value('image_format'),
        'quality': field.get_value('image_quality'),
        'pre_converted_only': field.get_value('image_pre_converted_only')
      }

      if not options['pre_converted_only']:
        del options['pre_converted_only']

      parameters = '&'.join(('%s=%s' % (k, v) for k, v in options.items()
                             if v))
      if parameters:
        result["default"] = '%s?%s' % (result["default"], parameters)
    if meta_type == "FileField":
      # FileField contain blobs (FileUpload instances), which aren't seriazable,
      # thus trying to return it to the client, besides being useless, breaks
      # the hal API
      del result["default"]
    return result

  if meta_type == "DateTimeField":
    result.update({
      "date_only": field.get_value("date_only"),
      "ampm_time_style": field.get_value("ampm_time_style"),
      "timezone_style": field.get_value("timezone_style"),
      "allow_empty_time": field.get_value('allow_empty_time'),
      "hide_day": field.get_value('hide_day'),
      "hidden_day_is_last_day": field.get_value('hidden_day_is_last_day'),
    })
    date_value = result["default"]
    if not date_value and field.get_value('default_now'):
      date_value = DateTime()
    if same_type(date_value, DateTime()):
      # Serialize DateTime
      date_value = date_value.rfc822()
    elif isinstance(date_value, datetime.date):
      date_value = formatdate(time.mktime(date_value.timetuple()))
    result["default"] = date_value
    for subkey in ("year", "month", "day", "hour", "minute", "ampm", "timezone"):
      result["subfield_%s_key" % subkey] = traversed_document.Field_getSubFieldKeyDict(field, subkey, key=result["key"])
    return result

  if meta_type in ("RelationStringField", "MultiRelationStringField"):
    portal_type_list = field.get_value('portal_type')
    translated_portal_type = []
    jump_reference_list = []
    relation_sort = field.get_value('sort')
    kw = {}
    if portal_type_list:
      portal_type_list = [x[0] for x in portal_type_list]
      translated_portal_type = [Base_translateString(x) for x in portal_type_list]
      # ported from Base_jumpToRelatedDocument\n
      base_category = field.get_value('base_category')
      for k, v in field.get_value('parameter_list'):
        kw[k] = v

      accessor_name = 'get%sValueList' % \
        ''.join([part.capitalize() for part in base_category.split('_')])
      try:
        jump_reference_list = getattr(traversed_document, accessor_name)(
          portal_type=[x[0] for x in field.get_value('portal_type')],
          filter=kw
        ) or []
      except Unauthorized:
        jump_reference_list = []
        result.update({
          "editable": False
        })
    relation_query_kw = kw.copy()
    relation_query_kw['portal_type'] = portal_type_list
    query = url_template_dict["jio_search_template"] % {
      "query": make_query({"query": sql_catalog.buildQuery(relation_query_kw).asSearchTextExpression(sql_catalog)})
    }

    result.update({
      "url": getRealRelativeUrl(traversed_document),
      "translated_portal_types": translated_portal_type,
      "portal_types": portal_type_list,
      "query": query,
      "sort": relation_sort,
      "catalog_index": field.get_value('catalog_index'),
      "allow_jump": field.get_value('allow_jump'),
      "allow_creation": field.get_value('allow_creation'),
      "search_view": url_template_dict['traverse_generator_action'] % {
        "root_url": site_root.absolute_url(),
        "script_id": script.id,
        "relative_url": getRealRelativeUrl(traversed_document).replace("/", "%2F"),
        "view": "Base_viewRelatedObjectList",
        "extra_param_json": urlsafe_b64encode(
          json.dumps(ensureSerializable({
            'original_form_id': form.id,
            'field_id': field.id
        })))
      }
    })

    if not isinstance(result["default"], list):
      result["default"] = [result["default"], ]
    result["default"] = [ensureUTF8(x) for x in result["default"]]

    result.update({
      "relation_field_id": traversed_document.Field_getSubFieldKeyDict(field, "relation", key=result["key"]),
      "relation_item_key": traversed_document.Field_getSubFieldKeyDict(field, "item", key=result["key"]),
      "relation_item_relative_url": [jump_reference.getRelativeUrl() for jump_reference in jump_reference_list],
      "relation_item_uid": [jump_reference.getUid() for jump_reference in jump_reference_list],
    })
    return result

  if meta_type in ("CheckBoxField", "MultiCheckBoxField"):
    if meta_type == "MultiCheckBoxField":
      result["items"] = toBasicTypes(field.get_value("items"))
    return result

  if meta_type == "GadgetField":
    result.update({
      "url": field.get_value("gadget_url"),
      "sandbox": field.get_value("js_sandbox")
    })
    try:
      result["renderjs_extra"] = json.dumps(dict(field.get_value("renderjs_extra")))
    except KeyError:
      # Ensure compatibility if the products are not yet up to date
      result["renderjs_extra"] = json.dumps({})
    return result

  if meta_type == "ListBox":
    """Display list of objects with optional search/sort capabilities on columns from catalog.

    We might be inside a ReportBox which is inside a parent form BUT we still have access to
    the original REQUEST with sent POST values from the parent form. We can save those
    values into our query method and reconstruct them meanwhile calling asynchronous jio.allDocs.
    """
    _translate = Base_translateString

    # column definition in ListBox own value 'columns' is superseded by dynamic
    # column definition from Selection for specific Report ListBoxes; the same for editable_columns
    column_list = [(name, _translate(title)) for name, title in (selection_params.get('selection_columns', [])
                                                                 or field.get_value("columns"))]
    editable_column_list = [(name, _translate(title)) for name, title in (selection_params.get('editable_columns', [])
                                                                          or field.get_value("editable_columns"))]
    all_column_list = [(name, _translate(title)) for name, title in field.get_value("all_columns")]
    catalog_column_list = [(name, title)
                           for name, title in OrderedDict(column_list + all_column_list).items()
                           if sql_catalog.isValidColumn(name)]

    # try to get specified searchable columns and fail back to all searchable columns
    search_column_list = [(name, _translate(title))
                          for name, title in (field.get_value("search_columns") or catalog_column_list)
                          if sql_catalog.isValidColumn(name)]

    # try to get specified sortable columns and fail back to searchable fields
    sort_column_list = [(name, _translate(title))
                        for name, title in (selection_params.get('selection_sort_order', [])
                                            or field.get_value("sort_columns") or search_column_list)
                        if sql_catalog.isValidColumn(name)]
    # portal_type list can be overriden by selection too
    # since it can be intentionally empty we don't override with non-empty field value
    portal_type_list = selection_params.get("portal_type", field.get_value('portal_types'))
    # requirement: get only sortable/searchable columns which are already displayed in listbox
    # see https://lab.nexedi.com/nexedi/erp5/blob/HEAD/product/ERP5Form/ListBox.py#L1004
    # implemented in javascript in the end
    # see https://lab.nexedi.com/nexedi/erp5/blob/master/bt5/erp5_web_renderjs_ui/PathTemplateItem/web_page_module/rjs_gadget_erp5_listbox_js.js#L163
    default_params = dict(field.get_value('default_params'))  # default_params is a list of tuples
    default_params['ignore_unknown_columns'] = True
    # we abandoned Selections in RJS thus we mix selection query parameters into
    # listbox's default parameters
    default_params.update(selection_params)

    # ListBoxes in report view has portal_type defined already in default_params
    # in that case we prefer non_empty version
    list_method_query_dict = default_params.copy()
    if not list_method_query_dict.get("portal_type", []) and portal_type_list:
      list_method_query_dict["portal_type"] = [x[0] for x in portal_type_list]
    list_method_custom = None
    # Search for non-editable documents - all reports goes here
    # Reports have custom search scripts which wants parameters from the form
    # thus we introspect such parameters and try to find them in REQUEST
    list_method = field.get_value('list_method') or None
    list_method_name = list_method.getMethodName() if list_method is not None else ""
    if list_method_name not in ("", "portal_catalog", "searchFolder", "objectValues"):
      # we avoid accessing known protected objects and builtin functions above
      try:
        list_method = getattr(traversed_document, list_method_name)
      except (Unauthorized, AttributeError, ValueError) as error:
        # we are touching some specially protected (usually builtin) methods
        # which we will not introspect
        log('ListBox {!s} list_method {} is unavailable because of "{!s}"'.format(
          field, list_method_name, error), level=100)
    else:
      list_method = None

    # Put all ListBox's search method params from REQUEST to `default_param_json`
    # because old code expects synchronous render thus having all form's values
    # still in the request which is not our case because we do asynchronous rendering
    if list_method is not None:
      selectKwargsForCallable(list_method, list_method_query_dict, REQUEST)

    if (True):  # editable_column_list (we need that template fields resolution
                # (issued by existence of `form_relative_url`) always kicks in
      extra_param_dict = {
        # in case of a dialog the form_id points to previous form, otherwise current form
        "form_id": REQUEST.get('form_id', form.id)
      }
      # Proxy listbox id is an hardcoded parameter used in relation field listbox
      # For now, keep it hardcoded, until another use case is found to provide
      # a default extra_param_dict
      if REQUEST.get('proxy_listbox_id', None) is not None:
        extra_param_dict['proxy_listbox_id'] = REQUEST.get('proxy_listbox_id')
      list_method_custom = url_template_dict["custom_search_template"] % {
        "root_url": site_root.absolute_url(),
        "script_id": script.id,
        "relative_url": getRealRelativeUrl(traversed_document).replace("/", "%2F"),
        "form_relative_url": "%s/%s" % (getFormRelativeUrl(form), field.id),
        "list_method": list_method_name,
        "default_param_json": urlsafe_b64encode(
          json.dumps(ensureSerializable(list_method_query_dict))),
        "extra_param_json": urlsafe_b64encode(
          json.dumps(ensureSerializable(extra_param_dict)))
      }
      # once we imprint `default_params` into query string of 'list method' we
      # don't want them to propagate to the query as well
      list_method_query_dict = {}
    """
    # We commented out this part because of backward compatibility
    # The problem seems to be that template fields for listboxes are
    # used in the old UI even though they are not listed in "editable columns"
    elif (list_method_name == "portal_catalog"):
      pass
    elif (list_method_name == "searchFolder"):
      list_method_query_dict["parent_uid"] = traversed_document.getUid()
    else:
      list_method_custom = url_template_dict["custom_search_template_no_editable"] % {
        "root_url": site_root.absolute_url(),
        "script_id": script.id,
        "relative_url": traversed_document.getRelativeUrl().replace("/", "%2F"),
        "list_method": list_method_name,
        "default_param_json": urlsafe_b64encode(json.dumps(ensureSerializable(list_method_query_dict)))
      }
      list_method_query_dict = {}
    """

#     row_list = list_method(limit=lines, portal_type=portal_types,
#                            **default_params)
#     line_list = []
#     for row in row_list:
#       document = row.getObject()
#       line = {
#         "url": url_template_dict["document_hal"] % {
#           "root_url": site_root.absolute_url(),
#           "relative_url": document.getRelativeUrl(),
#           "script_id": script.id
#         }
#       }
#       for property, title in columns:
#         prop = document.getProperty(property)
#         if same_type(prop, DateTime()):
#           prop = "XXX Serialize DateTime"  
#         line[title] = prop
#         line["_relative_url"] = document.getRelativeUrl()
#       line_list.append(line)

    result.update({
      "column_list": column_list,
      "all_column_list": all_column_list,
      "search_column_list": search_column_list,
      "sort" :field.get_value('sort'),
      "sort_column_list": sort_column_list,
      "editable_column_list": editable_column_list,
      "show_anchor": field.get_value("anchor"),
      "show_select": field.get_value("select"),
      "portal_type": portal_type_list,
      "lines": field.get_value('lines'),
      "default_params": ensureSerializable(default_params),
      "list_method": list_method_name,
      "show_stat": field.get_value('stat_method') != "" or len(field.get_value('stat_columns')) > 0,
      "show_count": field.get_value('count_method') != "",
      "query": url_template_dict["jio_search_template"] % {
        "query": make_query({
          "query": sql_catalog.buildQuery(
            list_method_query_dict,
            ignore_unknown_columns=True).asSearchTextExpression(sql_catalog)})},
      "domain_root_list": [(x, Base_translateString(y)) for x, y in field.get_value("domain_root_list")],
      "selection_name": field.get_value('selection_name'),
      "checked_uid_list": portal.portal_selections.getSelectionCheckedUidsFor(field.get_value('selection_name'))

    })
    result["domain_dict"] = getDomainSelection([x[0] for x in result["domain_root_list"]])

    if (list_method_custom is not None):
      result["list_method_template"] = list_method_custom

    # In the context of a form validation,
    # the lines must be synchronously calculated to keep track of the request values
    # Reuse the same parameters which were used during the first rendering
    query_param_json = REQUEST.get("%s_query_param_json" % field.id, None)
    if (query_param_json is not None) and (response.getStatus() == 400):
      result["default"] = json.loads(
        context.ERP5Document_getHateoas(mode='search',
          **ensureDeserialized(byteify(json.loads(urlsafe_b64decode(query_param_json))))
          )
      )

    return result

  if meta_type == "FormBox":
    embedded_document = {
      '_links': {},
      '_actions': {},
    }

    # FormBox might have own context if 'context_method_id' is defined
    formbox_context = REQUEST.get('cell', traversed_document)
    if field.get_value('context_method_id'):
      # harness acquisition and call the method right away
      formbox_context = getattr(traversed_document, field.get_value('context_method_id'))(
        field=field, REQUEST=REQUEST)
      embedded_document['_debug'] = "Different context"
    # get embedded form definition
    embedded_form_id = field.get_value('formbox_target_id')
    embedded_form = None
    if embedded_form_id:
      embedded_form = getattr(formbox_context, embedded_form_id, None)

    if embedded_form is None:
      # Do not trigger the formbox rendering
      result['type'] = 'BrokenFormBox'
      return result

    # renderForm mutates `embedded_document` therefor no return/assignment
    renderForm(formbox_context, embedded_form, embedded_document, key_prefix=key)
    # fix editability which is hard-coded to 0 in `renderForm` implementation
    embedded_document['form_id']['editable'] = field.get_value("editable")

    # update result with rendered sub-form
    result['_embedded'] = {
      '_view': embedded_document
    }
    return result

  if meta_type == "MatrixBox":
    # data are generated by python code for MatrixBox.py
    # template_fields are better rendered here because they can be part of "hidden"
    #                 group which is not rendered in form by default. Including
    #                 those fields directly here saves a lot of headache later
    template_field_names = ["{}_{}".format(field.id, editable_attribute)
      for editable_attribute, _ in field.get_value('editable_attributes')]
    result.update({
      'data': field.render(key=key, value=value, REQUEST=REQUEST, render_format='list'),
      'template_field_dict': {template_field: renderField(traversed_document, getattr(form, template_field), form)
        for template_field in template_field_names
        if template_field in form},
    })
    return result

  # All other fields are not implemented and we'll return only basic info about them
  result["_debug"] = "Unknown field type " + meta_type
  return result


def renderForm(traversed_document, form, response_dict, key_prefix=None, selection_params=None, extra_param_json=None):
  """
  Render a `form` in plain python dict.

  This function sets variables 'here' and 'form_id' resp. 'dialog_id' for forms resp. form dialogs to REQUEST.
  Any other REQUEST mingling are at the responsability of the callee.

  :param selection_params: holds parameters to construct ERP5Form.Selection instance
      for underlying ListBox - since we do not use selections in RenderJS UI
      we mitigate the functionality here by overriding ListBox's own values
      for columns, editable columns, and sort with those found in `selection_params`
  """
  previous_request_other = {}
  REQUEST.set('here', traversed_document)

  if extra_param_json is None:
    extra_param_json = {}

  # Following pop/push of form_id resp. dialog_id is here because of FormBox - an embedded form in a form
  # Fields of forms use form_id in their TALES expressions and obviously FormBox's form_id is different
  # from its parent's form. It is very important that we do not remove form_id in case of a Dialog Form.
  if form.pt == "form_dialog":
    previous_request_other['dialog_id'] = REQUEST.other.pop('dialog_id', None)
    REQUEST.set('dialog_id', form.id)
  else:
    previous_request_other['form_id'] = REQUEST.other.pop('form_id', None)
    REQUEST.set('form_id', form.id)

  field_errors = REQUEST.get('field_errors', {})

  include_action = True
  if form.pt == 'form_dialog':
    action_to_call = "Base_callDialogMethod"
  else:
    action_to_call = form.action
  if (not action_to_call) or \
     ((action_to_call == 'Base_edit') and (not portal.portal_membership.checkPermission('Modify portal content', traversed_document))):
    # prevent allowing editing if user doesn't have permission
    include_action = False

  if (include_action):
    # Form action
    response_dict['_actions'] = {
      'put': {
        "href": url_template_dict["form_action"] % {
          "traversed_document_url": site_root.absolute_url() + "/" + getRealRelativeUrl(traversed_document),
          "action_id": action_to_call
        },
        "action": form.action,
        "method": form.method,
      }
    }

  if form.pt == "form_dialog":
    # If there is a "form_id" in the REQUEST then it means that last view was actually a form
    # and we are most likely in a dialog. We save previous form into `last_form_id` ...
    last_form_id =  extra_param_json.pop("form_id", "") or REQUEST.get("form_id", "")
    last_listbox = None
    # ... so we can do some magic with it (especially embedded listbox if exists)!
    try:
      if last_form_id:
        last_form = getattr(context, last_form_id)
        last_listbox = last_form.Base_getListbox()
    except AttributeError:
      pass
    REQUEST.set("form_id", last_form_id)  # to be accessible in field rendering (namely ListBox)

  # Form traversed_document
  response_dict['_links']['traversed_document'] = {
    "href": default_document_uri_template % {
      "root_url": site_root.absolute_url(),
      "relative_url": getRealRelativeUrl(traversed_document),
      "script_id": script.id
    },
    "name": getRealRelativeUrl(traversed_document),
    "title": ensureUTF8(traversed_document.getTitle())
  }

  form_relative_url = getFormRelativeUrl(form)

  # Kept for compatibility
  response_dict['_links']['form_definition'] = {
    "href": default_document_uri_template % {
      "relative_url": form_relative_url
    },
    'name': form.id
  }

  response_dict['_embedded'] = {
    'form_definition': calculateHateoas(
      traversed_document=form,
      relative_url=form_relative_url,
      is_site_root=False,
      is_portal=False,
      mode='traverse',
      restricted=restricted,
      view='view'
    )
  }

  use_relation_form_page_template = (form.pt == "relation_form")
  if use_relation_form_page_template:
    # Provide the list of possible listboxes
    proxy_form_id_list = context.Base_getRelatedObjectParameter('proxy_listbox_ids')
    if not len(proxy_form_id_list):
      proxy_form_id_list = [('Base_viewRelatedObjectListBase/listbox', 'default')]

    # Create the possible choices
    root_url = site_root.absolute_url()
    renderHiddenField(response_dict, "proxy_form_id_list", '')
    response_dict["proxy_form_id_list"].update({
      "items": [(Base_translateString(y), url_template_dict['traverse_generator_action'] % {
        "root_url": site_root.absolute_url(),
        "script_id": script.id,
        "relative_url": getRealRelativeUrl(traversed_document).replace("/", "%2F"),
        "view": "Base_viewRelatedObjectList",
        "extra_param_json": urlsafe_b64encode(
          json.dumps(ensureSerializable({
            'proxy_listbox_id': x,
            'original_form_id': extra_param_json['original_form_id'],
            'field_id': extra_param_json['field_id']
          })))
      }) for x, y in proxy_form_id_list],
      "first_item": 1,
      "required": 0,
      "type": "ListField",
      "title": Base_translateString("Select Template")
    })

    # Allow to correctly render the listbox
    if REQUEST.get('proxy_listbox_id', None) is None:
      REQUEST.set('proxy_listbox_id', proxy_form_id_list[0][0])
    else:
      # Correctly set the listfield default value
      response_dict["proxy_form_id_list"]["default"] = url_template_dict['traverse_generator_action'] % {
        "root_url": site_root.absolute_url(),
        "script_id": script.id,
        "relative_url": getRealRelativeUrl(traversed_document).replace("/", "%2F"),
        "view": "Base_viewRelatedObjectList",
        "extra_param_json": urlsafe_b64encode(
          json.dumps(ensureSerializable({
            'proxy_listbox_id': REQUEST.get('proxy_listbox_id', None),
            'original_form_id': extra_param_json['original_form_id'],
            'field_id': extra_param_json['field_id']
          })))
      }

  # Go through all groups ("left", "bottom", "hidden" etc.) and add fields from
  # them into form.
  for group in form.Form_getGroupTitleAndId():
    # Skipping hidden group could be problematic but see MatrixBox Field above
    if 'hidden' in group['gid']:
      continue
    for field in form.get_fields_in_group(group['goid']):
      if not field.get_value("enabled"):
        continue
      try:
        response_dict[field.id] = renderField(traversed_document, field, form, key_prefix=key_prefix, selection_params=selection_params, request_field=not use_relation_form_page_template)
        if field_errors.has_key(field.id):
          response_dict[field.id]["error_text"] = field_errors[field.id].error_text
      except AttributeError as error:
        # Do not crash if field configuration is wrong.
        log("Field {} rendering failed because of {!s}".format(field.id, error), level=800)

  # Form Edit handler uses form_id to recover the submitted form and to control its
  # properties like editability
  if form.pt == 'form_dialog':
    # overwrite "form_id" field's value because old UI does that by passing
    # the form_id in query string and hidden fields
    renderHiddenField(response_dict, "form_id", last_form_id)
    if (last_listbox is not None):
      try:
        current_listbox = form.Base_getListbox()
      except AttributeError:
        current_listbox = None
      if (current_listbox is None):
        # If dialog has a listbox, do not return selection name
        # or it will lead to unexpected selection name
        last_selection_name = last_listbox.get_value('selection_name')
        renderHiddenField(response_dict, "selection_name", last_selection_name)
    # dialog_id is a mandatory field in any form_dialog
    renderHiddenField(response_dict, 'dialog_id', form.id)
    # some dialog actions use custom cancel_url
    if REQUEST.get('cancel_url', None):
      renderHiddenField(response_dict, "cancel_url", REQUEST.get('cancel_url'))

  else:
    # In form_view we place only form_id in the request form
    renderHiddenField(response_dict, 'form_id', form.id)

  if (form.pt == 'report_view'):
    # reports are expected to return list of ReportSection which is a wrapper
    # around a form - thus we will need to render those forms
    report_item_list = []
    report_result_list = []
    for field in form.get_fields():
      if field.getRecursiveTemplateField().meta_type == 'ReportBox':
        # ReportBox.render returns a list of ReportSection classes which are
        # just containers for FormId(s) usually containing one ListBox
        # and its search/query parameters hidden in `selection_params`
        # `path` contains relative_url of intended CONTEXT for underlying ListBox
        report_item_list.extend(field.render())
    # ERP5 Report document differs from a ERP5 Form in only one thing: it has
    # `report_method` attached to it - thus we call it right here
    if hasattr(form, 'report_method') and getattr(form, 'report_method', ""):
      report_method_name = getattr(form, 'report_method')
      report_method = getattr(traversed_document, report_method_name)
      report_item_list.extend(report_method())

    for report_index, report_item in enumerate(report_item_list):
      report_context = report_item.getObject(traversed_document)
      report_prefix = 'x%s' % report_index
      report_title = report_item.getTitle()
      # report_class = "report_title_level_%s" % report_item.getLevel()
      report_form_id = report_item.getFormId()
      report_form = getattr(report_context, report_form_id)
      report_result = {'_links': {}}
      # some reports save a lot of unserializable data (datetime.datetime) and
      # key "portal_type" (don't confuse with "portal_types" in ListBox) into
      # report_item.selection_params thus we need to take that into account in
      # ListBox field
      #
      # Selection Params are parameters for embedded ListBox's List Method
      # and it must be passed in `default_json_param` field (might contain
      # unserializable data types thus we need to take care of that
      # In order not to lose information we put all ReportSection attributes
      # inside the report selection params
      report_form_params = report_item.selection_params.copy() \
                           if report_item.selection_params is not None \
                           else {}

      # request.prefixed_selection_name maybe used in tales expression to display correct title of a ListBox
      if report_form is not None:
        listbox = getattr(report_form, 'listbox', None)
        if listbox is not None:
          listbox_selection_name = report_prefix + "_" + listbox.get_value('selection_name')
          REQUEST.other['prefixed_selection_name'] = listbox_selection_name
          if report_form_params:
            params = portal.portal_selections.getSelectionParamsFor(listbox_selection_name)
            params.update(report_form_params)
            portal.portal_selections.setSelectionParamsFor(listbox_selection_name, params)

      # report can have its own selection apart from embedded listboxes who have their own selections as well
      if report_item.selection_name:
        selection_name = report_prefix + "_" + report_item.selection_name
        report_form_params.update(selection_name=selection_name)
        # this should load selections with correct values - since it is modifying
        # global state in the backend we have nothing more to do here
        # I could not find where the code stores params in selection with render
        # prefix - maybe it in some `render` method where it should not be
        # Of course it is ugly, terrible and should be removed!
        selection_tool = context.getPortalObject().portal_selections
        selection_tool.getSelectionFor(selection_name, REQUEST)
        selection_tool.setSelectionParamsFor(selection_name, report_form_params)
        selection_tool.setSelectionColumns(selection_name, report_item.selection_columns)

      if report_item.selection_columns:
        report_form_params.update(selection_columns=report_item.selection_columns)
      if report_item.selection_sort_order:
        report_form_params.update(selection_sort_order=report_item.selection_sort_order)

      # Report section is just a wrapper around form thus we render it right
      # we keep traversed_document because its Portal Type Class should be
      # addressable by the user = have actions (object_view) attached to it
      # BUT! when Report Section defines `path` that is the new context for
      # form rendering and subsequent searches...
      renderForm(traversed_document if not report_item.path else report_context,
                 report_form,
                 report_result,
                 key_prefix=report_prefix,
                 selection_params=report_form_params)  # used to be only report_item.selection_params
      # Report Title is important since there are more section on report page
      # but often they render the same form with different data so we need to
      # distinguish by the title at least.
      report_result['title'] = report_title
      report_result_list.append(report_result)
    response_dict['report_section_list'] = report_result_list
  # end-if report_section

  for key, value in byteify(previous_request_other.items()):
    if value is not None:
      REQUEST.set(key, value)


def renderFormDefinition(form, response_dict):
  """Form "definition" is configurable in Zope admin: Form -> Order.

  We add some known constants inside Forms such as form_id and into
  Dialog Form such as dialog_id.
  """
  group_list = []
  for group in form.Form_getGroupTitleAndId():

    if group['gid'].find('hidden') < 0:
      field_list = []

      for field in form.get_fields_in_group(group['goid'], include_disabled=1):
        field_list.append((field.id, {'meta_type': field.meta_type}))

      group_list.append((group['gid'], field_list))

  # some forms might not have any fields so we put empty bottom group
  if not group_list:
    group_list = [('bottom', [])]

  # each form has hidden attribute `form_id`
  group_list[-1][1].append(('form_id', {'meta_type': 'StringField'}))

  if form.pt == "form_dialog":
    # every form dialog has its dialog_id and meta (control) attributes in extra_param_json
    group_list[-1][1].extend([
      ('selection_name', {'meta_type': 'StringField'}),
      ('dialog_id', {'meta_type': 'StringField'}),
      ('extra_param_json', {'meta_type': 'StringField'})
    ])

  response_dict["group_list"] = group_list
  response_dict["title"] = Base_translateString(form.getTitle())
  response_dict["pt"] = form.pt
  response_dict["action"] = form.action
  response_dict["action_title"] = Base_translateString(form.action_title)
  response_dict["update_action"] = form.update_action
  response_dict["update_action_title"] = Base_translateString(form.update_action_title)

def statusLevelToString(level):
  """Transform any level format to lowercase string representation"""
  if isinstance(level, (str, unicode)):
    if level.lower() == "error":
      return "error"
    elif level.lower().startswith("warn"):
      return "error"  # we might want to add another level for warning
    else:
      return "success"
  if level == ERROR:
    return "error"
  elif level == WARNING:
    return "error"
  else:
    return "success"


def calculateHateoas(is_portal=None, is_site_root=None, traversed_document=None, REQUEST=None,
                     response=None, view=None, mode=None,
                     query=None, select_list=None, limit=None, form=None,
                     relative_url=None, restricted=None, list_method=None,
                     default_param_json=None, form_relative_url=None, extra_param_json=None):

  if (restricted == 1) and (portal.portal_membership.isAnonymousUser() and (response is not None)):
    login_relative_url = site_root.getLayoutProperty("configuration_login", default="")
    if (login_relative_url):
      response.setHeader(
        'WWW-Authenticate',
        'X-Delegate uri="%s"' % (url_template_dict["login_template"] % {
          "root_url": site_root.absolute_url(),
          "login": login_relative_url
        })
      )
    response.setStatus(401)
    return ""

  if (view is not None):
    view = str(view)

  if relative_url:
    is_site_root = False
    if traversed_document is None:
      traversed_document = site_root.restrictedTraverse(relative_url, None)
      if (traversed_document is None):
        response.setStatus(404)
        return ""
  elif traversed_document is None:
    traversed_document = context

  # Check if traversed_document is the site_root
  if is_site_root is None:
    is_site_root = (traversed_document.getPath() == site_root.getPath())
  if is_portal is None:
    is_portal = (traversed_document.getPath() == portal.getPath())

  if mime_type != traversed_document.Base_handleAcceptHeader([mime_type]):
    response.setStatus(406)
    return ""

  # extra_param_json holds parameters for search interpreted by getHateoas itself
  # not by the list_method neither url_columns - only getHateoas
  if extra_param_json is None:
    extra_param_json = {}

  result_dict = {
    '_debug': mode,
    '_links': {
      "self": {
        # XXX Include query parameters
        # FIXME does not work in case of bulk queries
        "href": traversed_document.Base_getRequestUrl()
      },
      # Always inform about site root
      "site_root": {
        "href": default_document_uri_template % {
          "root_url": site_root.absolute_url(),
          "relative_url": site_root.getRelativeUrl(),
          "script_id": script.id
        },
        "name": site_root.getTitle(),
      },
      # Always inform about portal
      "portal": {
        "href": default_document_uri_template % {
          "root_url": portal.absolute_url(),
          # XXX the portal has an empty getRelativeUrl. Make it still compatible
          # with restrictedTraverse
          "relative_url": portal.getId(),
          "script_id": script.id
        },
        "name": portal.getTitle(),
      }
    }
    # possible other attributes
    # _notification {dict} form of {'message': "", 'status': ""}
    # _embedded {dict} form of {"_view": <erp5_document_properties>}
  }

  # Inject notification into response no matter the kind of request
  if portal_status_message:
    result_dict['_notification'] = {
      'message': str(portal_status_message),
      'status': statusLevelToString(portal_status_level)
    }

  if (mode == 'root') or (mode == 'traverse'):
    ##
    # Render ERP Document with a `view` specified
    # `view` contains view's name and we extract view's URL (we suppose form ${object_url}/Form_view)
    # which after expansion gives https://<site-root>/context/view_id?optional=params

    if (REQUEST is not None) and (REQUEST.other['method'] != "GET"):
      response.setStatus(405)
      return ""

    # Default properties shared by all ERP5 Document and Site
    current_action = {}  # current action parameters (context, script, URL params)
    action_dict = {}  # actions available on current `traversed_document`
    last_form_id = None  # will point to the previous form so we can obtain previous selection

    result_dict['title'] = ensureUTF8(traversed_document.getTitle())

    # extra_param_json should be base64 encoded JSON at this point
    # only for mode == 'form' it is already a dictionary
    if not extra_param_json:
      extra_param_json = {}

    if isinstance(extra_param_json, str):
      extra_param_json = ensureDeserialized(byteify(json.loads(urlsafe_b64decode(extra_param_json))))

    for k, v in byteify(extra_param_json.items()):
      REQUEST.set(k, v)

    # Add a link to the portal type if possible
    if not is_portal:
      # traversed_document should always have its Portal Type in ERP5 Portal Types
      # thus attached actions to it so it is viewable
      document_type_name = traversed_document.getPortalType()
      document_type = getattr(portal.portal_types, document_type_name, None)
      if document_type is not None:
        result_dict['_links']['type'] = {
          "href": default_document_uri_template % {
            "root_url": site_root.absolute_url(),
            "relative_url": document_type.getRelativeUrl(),
            "script_id": script.id
          },
          "name": Base_translateString(traversed_document.getPortalType())
        }

    # Return info about container
    if not is_portal:
      container = traversed_document.getParentValue()
      if container != portal:
        # Jio does not support fetching the root document for now
        result_dict['_links']['parent'] = {
          "href": default_document_uri_template % {
            "root_url": site_root.absolute_url(),
            "relative_url": container.getRelativeUrl(),
            "script_id": script.id
          },
          "name": Base_translateString(container.getTitle()),
        }

    # Find current action URL and extract embedded view
    erp5_action_dict = portal.Base_filterDuplicateActions(
      portal.portal_actions.listFilteredActionsFor(traversed_document))
    for erp5_action_key in erp5_action_dict.keys():
      for view_action in erp5_action_dict[erp5_action_key]:
        # Try to embed the form in the result
        if (view == view_action['id']):
          current_action = parseActionUrl('%s' % view_action['url'])  # current action/view being rendered

    if view and (view != 'view') and (current_action.get('view_id', None) is None):
      # XXX Allow to directly render a form
      current_action['view_id'] = view
      current_action['url'] = '%s/%s' % (getRealRelativeUrl(traversed_document), view)
      current_action['params'] = {}

    # If we have current action definition we are able to render embedded view
    # which should be a "ERP5 Form" but in reality can be anything
    if current_action.get('view_id', ''):
      view_instance = getattr(traversed_document, current_action['view_id'])
      if (view_instance is not None):
        embedded_dict = {
          '_links': {
            'self': {
              'href': current_action['url']
            }
          }
        }

        # Put all query parameters (?reset:int=1&workflow_action=start_action) in request to mimic usual form display
        # Request is later used for method's arguments discovery so set URL params into REQUEST (just like it was sent by form)
        for query_key, query_value in byteify(current_action['params'].items()):
          REQUEST.set(query_key, query_value)

        # If our "form" is actually a Script (nothing is sure in ERP5) or anything else than Form
        # (e.g. function or bound class method will) not have .meta_type thus be considered a Script
        # then we execute it directly
        if "Script" in getattr(view_instance, "meta_type", "Script"):
          view_instance = getattr(traversed_document, 'Base_viewFakePythonScriptActionForm')

        if view_instance.pt == "form_dialog":
          # If there is a "form_id" in the REQUEST then it means that last view was actually a form
          # and we are most likely in a dialog. We save previous form into `last_form_id` ...
          last_form_id =  REQUEST.get('form_id', "")

        # Sometimes callables (form dialog's method, listbox's list method...) do not touch
        # REQUEST but expect all (formerly) URL query parameters to appear in their **kw
        # thus we send extra_param_json (=rjs way of passing parameters to REQUEST) as
        # selection_params so they get into callable's **kw.
        renderForm(traversed_document, view_instance, embedded_dict,
                   selection_params=extra_param_json, extra_param_json=extra_param_json)

        if view_instance.pt == "form_python_action":
          for k, v in current_action['params'].items():
            renderHiddenField(embedded_dict, k, v)
            embedded_dict['_embedded']['form_definition']['group_list'][-1][1].append((k, {'meta_type': 'StringField'}))

          # Form action
          embedded_dict['_actions'] = {
            'put': {
              "href": url_template_dict["form_action"] % {
                "traversed_document_url": site_root.absolute_url() + "/" + getRealRelativeUrl(traversed_document),
                "action_id": current_action['view_id']
              }
            },
            "action": current_action['view_id'],
            "method": 'POST'
          }

        result_dict['_embedded'] = {
          '_view': embedded_dict
        }

    # Extract & modify action URLs
    for erp5_action_key in erp5_action_dict.keys():
      erp5_action_list = []
      for view_action in erp5_action_dict[erp5_action_key]:
        # Action condition is probably checked in Base_filterDuplicateActions
        erp5_action_list.append({
          'href': '%s' % view_action['url'],
          'name': view_action['id'],
          'icon': view_action['icon'],
          'title': Base_translateString(view_action['title'])
        })

        global_action_type = ("view", "workflow", "object_new_content_action",
                              "object_clone_action", "object_delete_action",
                              "object_list_action")
        if (erp5_action_key == view_action_type or
            erp5_action_key in global_action_type or
            "_jio" in erp5_action_key):

          # select correct URL template based on action_type and form page template
          url_template_key = "traverse_generator"
          if erp5_action_key not in ("view", "object_view", "object_jio_view"):
            url_template_key = "traverse_generator_action"
          # but when we do not have the last form id we do not pass is of course
          if not (current_action.get('view_id', '') or last_form_id):
            url_template_key = "traverse_generator"

          # some dialogs need previous form_id when rendering to pass UID to embedded Listbox
          extra_param_json['form_id'] = current_action['view_id'] \
            if current_action.get('view_id', '') and view_instance.pt in ("form_view", "form_list") \
            else last_form_id

          erp5_action_list[-1]['href'] = url_template_dict[url_template_key] % {
                "root_url": site_root.absolute_url(),
                "script_id": script.id,                                   # this script (ERP5Document_getHateoas)
                "relative_url": getRealRelativeUrl(traversed_document).replace("/", "%2F"),
                "view": erp5_action_list[-1]['name'],
                "extra_param_json": urlsafe_b64encode(json.dumps(ensureSerializable(extra_param_json)))
              }

        if erp5_action_key == 'object_jump':
          if 'Base_jumpToRelatedObject?' in view_action['url']:
            # Fetch the URL arguments
            # XXX Correctly unquote arguments
            argument_dict = dict([x.split('=') for x in view_action['url'].split('?', 1)[1].split("&")])
            jump_portal_type = argument_dict.pop('portal_type', None)
            if (jump_portal_type is not None):
              jump_portal_type = jump_portal_type.replace('+', ' ')
            final_argument_dict = {'portal_type': jump_portal_type}
            jump_related = argument_dict.pop('related', 1)
            if (jump_related):
              jump_related_suffix = ''
            else:
              jump_related_suffix = 'related_'

            jump_uid = portal.restrictedTraverse(argument_dict.pop('jump_from_relative_url', getRealRelativeUrl(traversed_document))).getUid()
            final_argument_dict['default_%s_%suid' % (argument_dict.pop('base_category'), jump_related_suffix)] = jump_uid

            erp5_action_list[-1]['href'] = url_template_dict["jio_search_template"] % {
              "query": make_query({"query": sql_catalog.buildQuery(final_argument_dict).asSearchTextExpression(sql_catalog)})
            }
          else:
            # XXX How to handle all custom jump actions?
            erp5_action_list.pop(-1)

      if erp5_action_list:
        if len(erp5_action_list) == 1:
          erp5_action_list = erp5_action_list[0]

        if erp5_action_key == view_action_type:
          # Configure view tabs on server level
          result_dict['_links']["view"] = erp5_action_list

        # Put a prefix to prevent conflict
        result_dict['_links']["action_" + erp5_action_key] = erp5_action_list

    ##############
    # XXX Custom slapos code
    ##############
    if is_site_root:
  
      result_dict['default_view'] = 'view'
      REQUEST.set("X-HATEOAS-CACHE", 1)
  
      # Global action users for the jIO plugin
      # XXX Would be better to not hardcode them but put them as portal type
      # "actions" (search could be on portal_catalog document, traverse on all
      # documents, newContent on all, etc)
  #     result_dict['_links']['object_search'] = {
  #       'href': '%s/ERP5Site_viewSearchForm?portal_skin=Hal' % absolute_url,
  #       'name': 'Global Search'
  #     }
      result_dict['_links']['raw_search'] = {
        "href": url_template_dict["search_template"] % {
          "root_url": site_root.absolute_url(),
          "script_id": script.id
        },
        'name': 'Raw Search',
        'templated': True
      }
      result_dict['_links']['traverse'] = {
        "href": url_template_dict["traverse_template"] % {
          "root_url": site_root.absolute_url(),
          "script_id": script.id
        },
        'name': 'Traverse',
        'templated': True
      }
      action_dict['add'] = {
        "href": url_template_dict["new_content_action"] % {
          "root_url": site_root.absolute_url(),
          "script_id": script.id
        },
        'method': 'POST',
        'name': 'New Content',
      }
      action_dict['bulk'] = {
        "href": url_template_dict["bulk_action"] % {
          "root_url": site_root.absolute_url(),
          "script_id": script.id
        },
        'method': 'POST',
        'name': 'Bulk'
      }
  
      # Handle also other kind of users: instance, computer, master
      person = portal.portal_membership.getAuthenticatedMember().getUserValue()
      if person is not None and portal.portal_membership.checkPermission('View', person):
        result_dict['_links']['me'] = {
          "href": default_document_uri_template % {
            "root_url": site_root.absolute_url(),
            "relative_url": person.getRelativeUrl(), 
            "script_id": script.id
          },
  #         '_relative_url': person.getRelativeUrl()
        }
  
    else:
      traversed_document_portal_type = traversed_document.getPortalType()
      if traversed_document_portal_type in ("ERP5 Form", "ERP5 Report"):
        renderFormDefinition(traversed_document, result_dict)
        if response is not None:
          response.setHeader("Cache-Control", "private, max-age=1800")
          response.setHeader("Vary", "Cookie,Authorization,Accept-Encoding")
          response.setHeader("Last-Modified", DateTime().rfc822())
          REQUEST.set("X-HATEOAS-CACHE", 1)
      elif relative_url == 'portal_workflow':
        result_dict['_links']['action_worklist'] = {
          "href": url_template_dict['worklist_template'] % {
            "root_url": site_root.absolute_url(),
            "script_id": script.id
          }
        }

      elif relative_url == 'portal_preferences':
        preference_tool = portal.portal_preferences
        preference = traversed_document.getActiveUserPreference()
        if preference:
          result_dict['_links']['active_preference'] = {
            "href": default_document_uri_template % {
              "root_url": site_root.absolute_url(),
              "relative_url": preference.getRelativeUrl(),
              "script_id": script.id
            }
          }

      elif relative_url == 'acl_users':
        logout_relative_url = site_root.getLayoutProperty("configuration_logout", default="")
        if (logout_relative_url):
          result_dict['_links']['logout'] = {
            "href": url_template_dict['logout_template'] % {
              "root_url": site_root.absolute_url(),
              "logout": logout_relative_url,
              "template": True
            }
          }

    # Define document action
    if action_dict:
      result_dict['_actions'] = action_dict

  elif mode == 'search':
    #################################################
    # Portal catalog search
    #
    # Possible call arguments example:
    #  form_relative_url: portal_skins/erp5_web/WebSite_view/listbox
    #  list_method: "objectValues"                    (Script providing items)
    #  default_param_json: <base64 encoded JSON>      (Additional search params)
    #  query: <str>                                   (term for fulltext search)
    #  select_list: ['int_index', 'id', 'title', ...] (column names to select)
    #  limit: [15, 16]                                (begin_index, num_records)
    #  local_roles: TODO
    #  selection_domain: JSON string: {region: 'foo/bar'}
    #  extra_param_json: <base64 encoded JSON>        (paramters for getHateoas itself)
    #
    # Default Param JSON contains
    #  portal_type: list of Portal Types to include (singular form matches the
    #                                                catalog column name)
    #
    # Discussion:
    #
    #  Why you didn't use ListBoxRendererLine?
    #  > Method 'search' is used for getting related objects as well which are
    #  > not backed up by a ListBox thus the value resolution would have to be
    #  > there anyway. It is better to use one code for all in this case.
    #
    #  How do you deal with old-style Selections?
    #  > We simply do not use them. All Document selection is handled via passing
    #  > "query" parameter to Base_callDialogMethod or introspecting list_methods.
    #################################################
    if (not recursive_call) and (REQUEST.other['method'] != "GET"):
      response.setStatus(405)
      return ""

    # Those parameter will be send back during the listbox submission
    # to ensure fetching the same lines
    listbox_query_param_json = urlsafe_b64encode(json.dumps(ensureSerializable({
      'form_relative_url': form_relative_url,
      'list_method': list_method,
      'default_param_json': default_param_json,
      'query': query,
      'select_list': select_list,
      'limit': limit,
      'local_roles': local_roles,
      'selection_domain': selection_domain,
      'extra_param_json': extra_param_json,
      'relative_url': relative_url,
      'group_by': group_by,
      'sort_on': sort_on
    })))

    # set 'here' for field rendering which contain TALES expressions
    REQUEST.set('here', traversed_document)
    # Put all items from extra_param_json into the REQUEST. It is the only
    # way how we can keep state, which is required by some actions for example
    # search issued from dialog needs previous form_id because often it just
    # copies the previous search thus we need to pass it and we do not want
    # to introduce another parameter to getHateos so we reuse `form`
    # This is needed for example for erp5_core/Folder_viewDeleteDialog/listbox
    # (see TALES expression for form_id and field_id there)
    if not extra_param_json:
      extra_param_json = {}

    if isinstance(extra_param_json, str):
      extra_param_json = ensureDeserialized(byteify(json.loads(urlsafe_b64decode(extra_param_json))))

    for key, value in byteify(extra_param_json.items()):
      REQUEST.set(key, value)

    # in case we have custom list method
    catalog_kw = {}

    # form field issuing this search
    source_field = portal.restrictedTraverse(form_relative_url) if form_relative_url else None
    source_field_meta_type = source_field.meta_type if source_field is not None else ""
    if source_field_meta_type == "ProxyField":
      source_field_meta_type = source_field.getRecursiveTemplateField().meta_type
    is_rendering_listbox = (source_field is not None) and (source_field_meta_type == "ListBox")

    count_method = ""
    if is_rendering_listbox:
      count_method = source_field.get_value('count_method')
    has_listbox_a_count_method = (count_method != "") and (count_method.getMethodName() != list_method)

    # hardcoded responses for site and portal objects (which are not Documents!)
    # we let the flow to continue because the result of a list_method call can
    # be similar - they can in practice return anything
    if query == "__root__":
      search_result_iterable = [site_root]
    elif query == "__portal__":
      search_result_iterable = [portal]
    else:
      # otherwise gather kwargs for list_method and get whatever result it gives
      callable_list_method = portal.portal_catalog
      if list_method:
        callable_list_method = getattr(traversed_document, list_method)

      catalog_kw = {
        "local_roles": local_roles,
        "sort_on": ()  # default is an empty tuple
      }
      if default_param_json is not None:
        catalog_kw.update(
          ensureDeserialized(
            byteify(
              json.loads(urlsafe_b64decode(default_param_json)))))
      if query:
        catalog_kw["full_text"] = query

      if selection_domain is not None:
        selection_domain_dict = ensureDeserialized(
            byteify(json.loads(selection_domain)))
        category_tool = portal.portal_categories
        domain_tool = portal.portal_domains

        if is_rendering_listbox:
          new_selection_dict = {}

        for domain_root_id in selection_domain_dict:
          domain_root = category_tool.restrictedTraverse(domain_root_id, None)
          selection_path = selection_domain_dict[domain_root_id]
          if domain_root is None:
            selection_root = 'portal_domains'
            selection_domain_dict[domain_root_id] = domain_tool.getDomainByPath('%s/%s' % (domain_root_id, selection_domain_dict[domain_root_id]))
          else:
            selection_root = 'portal_categories'
            selection_domain_dict[domain_root_id] = domain_root.restrictedTraverse(selection_domain_dict[domain_root_id])

          if is_rendering_listbox:
            new_selection_dict[domain_root_id] = (selection_root, '%s/%s' % (domain_root_id, selection_path), )

        catalog_kw["selection_domain"] = selection_domain_dict

      if sort_on is not None:
        def parseSortOn(raw_string):
          """Turn JSON serialized array into a tuple (col_name, order)."""
          sort_col, sort_order = json.loads(raw_string)
          sort_col, sort_order = byteify(sort_col), byteify(sort_order)
          # The sort_order value comes from the listbox's definition. But for historical reason,
          # it often contains values like "Type | Type", instead of "Type | ASC".
          # In reality, "Type | Type" will be interpreted as "Type | ASC", because of the
          # catalog implementation :
          # https://lab.nexedi.com/nexedi/erp5/blob/3978dba1cfc3b68d85b5ebddebfdd3ff3177854d/product/ZSQLCatalog/SQLCatalog.py#L2115-2118
          # For consistency reasons, the code here should mirror this behavior
          if sort_order.lower() in ('desc', 'descending', 'reverse'):
            sort_order = "DESC"
          else:
            sort_order = "ASC"
          return (sort_col, sort_order)

        if isinstance(sort_on, list):
          # sort_on argument is always a list of tuples(col_name, order)
          catalog_kw['sort_on'] = list(map(parseSortOn, sort_on))
        else:
          catalog_kw['sort_on'] = [parseSortOn(sort_on), ]

      if group_by is not None:
        if isinstance(group_by, list):
          catalog_kw['group_by_list'] = group_by
        else:
          catalog_kw['group_by_list'] = [str(group_by)]
        # Include select, as user may want to count
        catalog_kw["select_list"] = select_list

      if limit:
        catalog_kw["limit"] = limit
      if is_rendering_listbox and not has_listbox_a_count_method:
        # When rendering a listbox without count method, add a dummy manual count
        # by fetching more documents than requested
        catalog_kw["limit"] = [0, COUNT_LIMIT]

      if is_rendering_listbox:
        # Store the current search parameters in the listbox selection
        # This is done to improve compatibility with existing actions (ODS style for example)
        # No need to edit current selection. Replace it with a new one
        selection_tool = portal.portal_selections
        selection_name = source_field.get_value('selection_name')
        selection_kw = {}

        selection_kw['method_path'] = '%s/%s' % (traversed_document.getPath(), list_method)
        selection_kw['params'] = {}
        if default_param_json is not None:
          selection_kw['params'].update(
            ensureDeserialized(
              byteify(
                json.loads(urlsafe_b64decode(default_param_json)))))
        selection_kw['params']['limit'] = COUNT_LIMIT
        selection_kw['params']['local_roles'] = catalog_kw["local_roles"]
        if 'full_text' in catalog_kw:
          selection_kw['params']['full_text'] = catalog_kw["full_text"]
        if 'sort_on' in catalog_kw:
          selection_kw['sort_on'] = catalog_kw['sort_on']

        if select_list:
          column_list = [(name, title) for name, title in source_field.get_value("columns") if name in select_list]
          all_column_list = [(name, title) for name, title in source_field.get_value("all_columns") if name in select_list]
          selection_kw['columns'] = [(name, Base_translateString(title))
                                     for name, title in OrderedDict(column_list + all_column_list).items()]
        else:
          selection_kw['columns'] = []

        selection_tool.setSelectionFor(selection_name, Selection(selection_name, **selection_kw))

        if 'selection_domain' in catalog_kw:
          selection_tool.setDomainDictFromParam(selection_name, new_selection_dict)

      # Some search scripts impertinently grab their arguments from REQUEST
      # instead of being nice and specify them as their input parameters.
      #
      # We expect that wise and mighty ListBox did copy all form field values
      # from its REQUEST into `default_param_json` so we can put them back.
      #
      # XXX Kato: Seems that current scripts are behaving nicely (using only
      # specified input parameters). In case some list_method does not work
      # this is the first place to try to uncomment.
      #
      # for k, v in catalog_kw.items():
      #   REQUEST.set(k, v)
      search_result_iterable = callable_list_method(**catalog_kw)

    # Cast to list if only one element is provided
    if select_list is None:
      select_list = []
    elif same_type(select_list, ""):
      select_list = [select_list]

    # extract form field definition into `editable_field_dict`
    editable_field_dict = {}
    url_column_dict = {}
    listbox_form = None
    listbox_field_id = None

    if is_rendering_listbox:
      listbox_field_id = source_field.id
      listbox_form = getattr(traversed_document, source_field.aq_parent.id)

      url_column_dict = dict(source_field.get_value('url_columns'))

      # support only selection_name for stat methods&url columns because any `selection` is deprecated
      # and should be removed. Selection_name can be passed in catalog_kw by e.g. reports so it has precedence.
      # Romain wants full backward compatibility so putting `selection` back in parameters
      selection_name = catalog_kw.get('selection_name', source_field.get_value('selection_name'))
      if selection_name and 'selection_name' not in catalog_kw:
        catalog_kw['selection_name'] = selection_name
      if 'selection' not in catalog_kw:
        catalog_kw['selection'] = context.getPortalObject().portal_selections.getSelectionFor(selection_name, REQUEST)

      # fill the proxy_field_stack
      proxy_field_stack = [source_field]  # last of the stack should not be a proxy field
      loop_protection_dict = {None: True, source_field: True}
      field_stack_iteration = source_field
      while field_stack_iteration.meta_type == "ProxyField":
        next_iteration = field_stack_iteration.getTemplateField()
        if next_iteration in loop_protection_dict:
          break
        loop_protection_dict[next_iteration] = True
        field_stack_iteration = next_iteration
        proxy_field_stack.append(field_stack_iteration)

      # fill editable_field_dict
      # See Products.ERP5Form.Listbox ListBoxRenderer.getEditableField method.
      # This method can not be used directly as `source_field` is a ProxyField instance (not a ListBoxRenderer instance).
      # It is unauthorized to import ListBoxRenderer.
      for select in select_list:
        for proxy_field in proxy_field_stack:
          proxy_field_id = proxy_field.id
          proxy_field_name = "{}_{}".format(proxy_field_id, select.replace(".", "_"))
          proxy_form = getattr(traversed_document, proxy_field.Base_aqInner().aq_parent.id)
          if proxy_form.has_field(proxy_field_name, include_disabled=1):
            editable_field_dict[select] = proxy_form.get_field(proxy_field_name, include_disabled=1)
            break

    # handle the case when list-scripts are ignoring `limit` - paginate for them
    if limit is not None:
      if isinstance(limit, (tuple, list)):
        start, num_items = map(int, limit)
      elif isinstance(limit, int):
        start, num_items = 0, limit
      else:
        start, num_items = 0, int(limit)
      if not (is_rendering_listbox and not has_listbox_a_count_method):
        # the limit was most likely taken into account thus we don't need to slice
        start, num_items = 0, len(search_result_iterable)
    else:
      start, num_items = 0, len(search_result_iterable)

    contents_list = []  # resolved fields from the search result
    result_dict.update({
      '_query': query,
      '_local_roles': local_roles,
      '_selection_domain': selection_domain,
      '_limit': limit,
      '_select_list': select_list,
      '_group_by': group_by,
      '_sort_on': sort_on,
      '_embedded': {}
    })

    Listbox_getBrainValue = traversed_document.Listbox_getBrainValue
    field_errors = REQUEST.get('field_errors', {})

    # Compatibility with Listbox.py ListMethodWrapper
    can_check_local_property = list_method not in ('objectValues', 'contentValues')
    # now fill in `contents_list` with actual information
    # beware that search_result_iterable can hide anything inside!
    for result_index, brain in enumerate(search_result_iterable):
      # skip documents out of `limit`
      if result_index < start:
        continue
      if result_index >= start + num_items:
        break

      # we can render fields which need 'here' to be set to currently rendered document
      #REQUEST.set('here', search_result)
      contents_item = {}
      try:
        brain_document = brain.getObject()
      except AttributeError:
        # This is not a ZSQLBrain/ERP5 Document
        brain_document = brain

        # means we are iterating over plain objects
        # list_method must be defined because POPOs can return only that
        brain_uid = "{}#{:d}".format(list_method, result_index)
        # JIO requires every item to have _links.self.href so it can construct
        # links to the document. Here we have a object in RAM (which should
        # never happen!) thus we provide temporary UID
        brain_relative_url = "{}/{}".format(getRealRelativeUrl(traversed_document), brain_uid)
      else:
        brain_uid = brain.uid
        brain_relative_url = getRealRelativeUrl(brain_document)

      # _links.self.href is mandatory for JIO so it can create reference to the
      # (listbox) item alone
      contents_item['_links'] = {
        'self': {
          "href": default_document_uri_template % {
            "root_url": site_root.absolute_url(),
            "relative_url": brain_relative_url,
            "script_id": script.id
          },
        },
      }

      # ERP5 stores&send the list of editable elements in a hidden field called
      # only database results can be editable so it belongs here
      if listbox_field_id:# and source_field.get_value("editable"):
        contents_item['listbox_uid:list'] = {
          'key': "%s_uid:list" % listbox_field_id,
          'value': brain_uid
        }

      is_getListItemUrlDict_calculated = False

      # Put 'cell' to REQUEST (expected by tales) and let the field evaluate
      # Needed to evaluate 'items' attribute of listfield for example
      REQUEST.set('cell', brain)
      for select in select_list:
        contents_item[select] = {}
        editable_field = editable_field_dict.get(select, None)
        default_field_value = Listbox_getBrainValue(
          brain,
          brain_document,
          select,
          can_check_local_property,
          editable_field=editable_field
        )

        if isinstance(default_field_value, Message):
          default_field_value = default_field_value.translate()

        if editable_field is None:
          # make resulting value JSON serializable
          if isinstance(default_field_value, DateTime):
            # Serialize DateTime
            default_field_value = default_field_value.rfc822()
            # XXX Kato: what exactly should the later mean?
          elif isinstance(default_field_value, datetime.date):
            default_field_value = formatdate(time.mktime(default_field_value.timetuple()))

          contents_item[select] = default_field_value

        else:
          # If the contents_item has field rendering in it, better is to add an
          # extra layer of abstraction to not get conflicts
          contents_item[select]['field_gadget_param'] = renderField(
            traversed_document,
            editable_field,
            listbox_form,
            value=default_field_value,
            key='field_%s_%s' % (editable_field.id, brain_uid))
          # Include cell error text in case of form validation
          if field_errors.has_key('%s_%s' % (editable_field.id, brain_uid)):
            contents_item[select]['field_gadget_param']["error_text"] = \
              field_errors['%s_%s' % (editable_field.id, brain_uid)].error_text


        # Do not generate link for empty value, as it will not be clickable in UI
        if default_field_value not in ('', None):
          # By default, we won't be generating views in the URL
          url_parameter_dict = None
          if select in url_column_dict:
            # Check if we get URL parameters using listbox field `url_columns`
            try:
              # XXX call on aq_base?
              url_column_method = getattr(brain, url_column_dict[select])
              # Result of `url_column_method` must be a dictionary in the format
              # {'command': <command_name, ex: 'raw', 'push_history'>,
              #  'options': {'url': <Absolute URL>, 'jio_key': <Relative URL of object>, 'view': <id of the view>}}
              url_parameter_dict = url_column_method(url_dict=True,
                                                     brain=brain,
                                                     selection=catalog_kw['selection'],
                                                     selection_name=catalog_kw['selection_name'],
                                                     column_id=select)
            except AttributeError as e:
              # In case the URL method is invalid or empty, we expect to have no link
              # for the column to maintain compatibility with old UI, hence we create
              # an empty url_parameter_dict for these cases.
              url_parameter_dict = {}
              if url_column_dict[select]:
                log("Invalid URL method {!s} on column {}".format(url_column_dict[select], select), level=800)

          else:
            if not is_getListItemUrlDict_calculated:
              # XXX If only available on brains, maybe better to call on aq_self
              getBrainListItemUrlDict = getattr(brain, 'getListItemUrlDict', None)
              is_getListItemUrlDict_calculated = True
            if getBrainListItemUrlDict is not None:
              # Check if we can get URL result from the brain
              try:
                url_parameter_dict = getBrainListItemUrlDict(
                  select, result_index, catalog_kw['selection_name']
                )
              except (ConflictError, RuntimeError):
                raise
              except:
                log('could not evaluate the url method getListItemUrlDict with %r' % brain,
                    level=800)

          if isinstance(url_parameter_dict, dict):
            # We need to put URL into rendered field so just ensure it is a dict
            if not isinstance(contents_item[select], dict):
              contents_item[select] = {
                'default': contents_item[select],
              }
            # We should be generating view if there is extra params for view in
            # view_kw. These parameters are required to create url at hateoas side
            # using the URL template as necessary
            if 'view_kw' not in url_parameter_dict:
              contents_item[select]['url_value'] = url_parameter_dict
            else:
              # Get extra parameters either from url_result_dict or from brain
              extra_url_param_dict = url_parameter_dict['view_kw'].get('extra_param_json', {})
              url_template_id = 'traverse_generator'
              if extra_url_param_dict:
                url_template_id = 'traverse_generator_action'

              # Explicity populate url_value dict. This way we can ensure that whatever been
              # sent via url_parameter_dict goes directly in url_value dict
              contents_item[select]['url_value'] = {}
              contents_item[select]['url_value']['command'] = url_parameter_dict['command']
              contents_item[select]['url_value']['options'] = url_parameter_dict['options']
              # Generate `view` to be used to construct URL
              contents_item[select]['url_value']['options']['view'] = url_template_dict[url_template_id] % {
                "root_url": site_root.absolute_url(),
                "script_id": script.id,
                "relative_url": url_parameter_dict['view_kw']['jio_key'].replace("/", "%2F"),
                "view": url_parameter_dict['view_kw']['view'],
                "extra_param_json": urlsafe_b64encode(
                  json.dumps(ensureSerializable(extra_url_param_dict)))
                }

      # endfor select
      REQUEST.other.pop('cell', None)
      contents_list.append(contents_item)
    result_dict['_embedded']['contents'] = ensureSerializable(contents_list)

    # Compute statistics if the search issuer was ListBox
    # or in future if the stats (SUM) are required by JIO call

    # Lets mingle with editability of fields here
    # Original Listbox.py modifies editability during field rendering (method `render`),
    # which is done on frontend side, so we overwrite result's own editability
    if is_rendering_listbox:
      editable_column_set = set(name for name, _ in source_field.get_value("editable_columns"))
      for line in result_dict['_embedded']['contents']:
        for select in line:
          # forbid editability only for fields not specified in editable_columns
          if select in editable_column_set:
            continue
          if isinstance(line[select], dict) and 'field_gadget_param' in line[select]:
            line[select]['field_gadget_param']['editable'] = False

      # Trigger count method if exist
      # XXX No need to count if no pagination
      if has_listbox_a_count_method:
        count_kw = dict(catalog_kw)
        # Drop not needed parameters
        count_kw.pop('selection', None)
        count_kw.pop('selection_name', None)
        count_kw.pop("sort_on", None)
        count_kw.pop("limit", None)
        try:
          count_method = getattr(traversed_document, count_method.getMethodName())
          count_method_result = count_method(REQUEST=REQUEST, **count_kw)
          result_dict['_embedded']['count'] = ensureSerializable(count_method_result[0][0])
        except AttributeError as error:
          # In case there is no count_method or some invalid mehtod, instead of
          # raising error and breaking the view, its better to log on as warning
          # and just pass. This also ensures we have compatibilty with how old
          # UI behave in these cases.
          log('Invalid count method %s' % error, level=800)
      else:
        result_dict['_embedded']['count'] = ensureSerializable(len(search_result_iterable))

      contents_stat_list = []
      # in case the search was issued by listbox we can provide results of
      # stat_method and count_method back to the caller
      # XXX: we should check whether they asked for it
      stat_method = source_field.get_value('stat_method')
      stat_columns = source_field.get_value('stat_columns')


      contents_stat = {}
      if len(stat_columns) > 0:
        # prefer stat per column (follow original ListBox.py implementation)
        for stat_name, stat_script in stat_columns:
          if stat_name in select_list:
            # Do not trigger potential expensive calculation if column is not displayed
            contents_stat[stat_name] = getattr(traversed_document, stat_script)(REQUEST=REQUEST, **catalog_kw)
        contents_stat_list.append(contents_stat)
      elif stat_method != "" and stat_method.getMethodName() != list_method:
        # general stat_method is second in priority list - should return dictionary or list of dictionaries
        # where all "fields" should be accessible by their "select" name (no "listbox_" prefix)
        stat_method_result = getattr(traversed_document, stat_method.getMethodName())(REQUEST=REQUEST, **catalog_kw)
        # stat method can return simple dictionary or subscriptable object thus we put it into one-item list
        if stat_method_result is not None and not isinstance(stat_method_result, (list, tuple)):
          stat_method_result = [stat_method_result, ]
        contents_stat_list = toBasicTypes(stat_method_result) or []

      for contents_stat in contents_stat_list:
        for key, value in contents_stat.items():
          if key in editable_field_dict:
            contents_stat[key] = renderField(
              traversed_document, editable_field_dict[key], listbox_form, value, key=editable_field_dict[key].id + '__sum')

      if len(contents_stat_list) > 0:
        result_dict['_embedded']['sum'] = ensureSerializable(contents_stat_list)

      # Those parameter will be send back during the listbox submission
      # to ensure fetching the same lines
      result_dict['_embedded']['listbox_query_param_json'] = {
        'key': "%s_query_param_json" % listbox_field_id,
        'value': listbox_query_param_json
      }

    # We should cleanup the selection if it exists in catalog params BUT
    # we cannot because it requires escalated Permission.'modifyPortal' so
    # the correct solution would be to ReportSection.popReport but unfortunately
    # we don't have it anymore because we are asynchronous
    return result_dict

  elif mode == 'form':
    #################################################
    # Calculate form value
    #################################################
    if REQUEST.other['method'] != "POST":
      response.setStatus(405)
      return ""

    renderForm(traversed_document, form, result_dict, extra_param_json=extra_param_json)

  elif mode == 'newContent':
    #################################################
    # Create new document
    #################################################
    if REQUEST.other['method'] != "POST":
      response.setStatus(405)
      return ""
    portal_type = REQUEST.form["portal_type"]
    parent_relative_url = REQUEST.form["parent_relative_url"]
    # First, try to validate the data on a temp document
    parent = portal.restrictedTraverse(parent_relative_url)
    # module = portal.getDefaultModule(portal_type=portal_type)
    document = parent.newContent(
      portal_type=portal_type
    )
    # http://en.wikipedia.org/wiki/Post/Redirect/Get
    response.setStatus(201)
    response.setHeader("X-Location",
      default_document_uri_template % {
        "root_url": site_root.absolute_url(),
        "relative_url": document.getRelativeUrl(),
        "script_id": script.id
      })
    return ''
  
  elif mode == 'bulk':
    #################################################
    # Return multiple documents in one request
    #################################################
    if REQUEST.other['method'] != "POST":
      response.setStatus(405)
      return ""
    result_dict["result_list"] = [calculateHateoas(mode="traverse", **x) for x in byteify(json.loads(bulk_list))]
  
  elif mode == 'worklist':
    #################################################
    # Return all worklist jio urls
    #################################################
    if REQUEST.other['method'] != "GET":
      response.setStatus(405)
      return ""
    action_list = portal.portal_workflow.WorkflowTool_listActionParameterList()
    checkPermission = portal.Base_checkPermission
    work_list = []
    for action in action_list:
      query = sql_catalog.buildQuery(action['query'])\
                         .asSearchTextExpression(sql_catalog)

      if (action['local_roles']):
        # Hack to consider local_roles as a valid catalog parameter
        role_query = sql_catalog.buildQuery({'simulation_state': action['local_roles']})\
                                .asSearchTextExpression(sql_catalog)

        query += ' AND %s' % role_query.replace('simulation_state', 'local_roles')
      worklist_dict = {
        'href': url_template_dict["jio_search_template"] % {
          "query": make_query({"query": query})
        },
        'name': Base_translateString(re.sub(r' \(\d+\)$', '', action['name'])),
        'count': action['count']
      }

      portal_type_list = action['query'].get('portal_type', None)
      if (portal_type_list):
        worklist_module_id = None
        if same_type(portal_type_list, ''):
          portal_type_list = [portal_type_list]

        for portal_type in portal_type_list:
          if (worklist_module_id is None):
            worklist_module_id = portal.getDefaultModuleId(portal_type, default=None, only_visible=False)
          elif (worklist_module_id != portal.getDefaultModuleId(portal_type, default=None, only_visible=False)):
            worklist_module_id = None
          if worklist_module_id is None:
            break

        if (worklist_module_id is not None and checkPermission(worklist_module_id, 'View')):
          worklist_dict['module'] = default_document_uri_template % {
            "relative_url": worklist_module_id
          }
      work_list.append(worklist_dict)

    result_dict["worklist"] = work_list

  else:
    raise NotImplementedError("Unsupported mode %s" % mode)
  
  return result_dict


mime_type = 'application/hal+json'
portal = context.getPortalObject()
sql_catalog = portal.portal_catalog.getSQLCatalog()

# Calculate the site root to prevent unexpected browsing
is_web_mode = (context.REQUEST.get('current_web_section', None) is not None) or (hasattr(context, 'isWebMode') and context.isWebMode())
# is_web_mode =  traversed_document.isWebMode()
if is_web_mode:
  site_root = context.getWebSectionValue()
  view_action_type = site_root.getLayoutProperty("configuration_view_action_category", default='object_view')
else:
  site_root = portal
  view_action_type = "object_view"

# Calculate view url
if mode == 'url_generator':
  #################################################
  # Allow to generator URL from other python scripts
  #################################################
  if REQUEST.other['method'] != "GET":
    response.setStatus(405)
    return ""
  if (keep_items is None):
    generator_key = 'traverse_generator'
    keep_items_json = None
  else:
    generator_key = 'traverse_generator_action'
    keep_items_json = urlsafe_b64encode(
      json.dumps(ensureSerializable(keep_items)))
  return url_template_dict[generator_key] % {
    "root_url": site_root.absolute_url(),
    "script_id": 'ERP5Document_getHateoas',
    "relative_url": relative_url.replace("/", "%2F"),
    "view": view,
    "extra_param_json": keep_items_json
  }

context.Base_prepareCorsResponse(RESPONSE=response)

response.setHeader('Content-Type', mime_type)
hateoas = calculateHateoas(relative_url=relative_url,
                           REQUEST=REQUEST, response=response, view=view, mode=mode,
                           query=query, select_list=select_list, limit=limit, form=form,
                           restricted=restricted, list_method=list_method,
                           default_param_json=default_param_json,
                           form_relative_url=form_relative_url,
                           extra_param_json=extra_param_json)
if hateoas == "":
  return hateoas
else:
  return json.dumps(hateoas, indent=2)
