"""Hello. This will be long because this goodness script does almost everything.

In general it always returns a JSON reponse in HATEOAS format specification.

:param REQUEST: HttpRequest holding GET and/or POST data
:param response:
:param view: either "view" or absolute URL of an ERP5 Action
:param mode: {str} help to decide what user wants from us "form" | "search" ...
:param relative_url: an URL of `traversed_document` to operate on (it must have an object_view)

Only in mode == 'search'
:param query: string-serialized Query
:param select_list: list of strings to select from search result object
:param limit: tuple(start_index, num_records) which is further passed to list_method BUT not every list_method takes it into account
:param form_relative_url: {str} relative URL of a form FIELD issuing the search (listbox/relation field...)
                          it can be None in case of special listboxes like List of Modules
                          or relative path like "portal_skins/erp5_ui_test/FooModule_viewFooList/listbox"

Only in mode == 'form'
:param form:

Only in mode == 'traverse'


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
from Products.ERP5Type.Utils import UpperCase
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery
from Products.ERP5Type.Log import log
from collections import OrderedDict

MARKER = []

if REQUEST is None:
  REQUEST = context.REQUEST
  # raise Unauthorized
if response is None:
  response = REQUEST.RESPONSE

# http://stackoverflow.com/a/13105359
def byteify(string):
  if isinstance(string, dict):
    return {byteify(key): byteify(value) for key, value in string.iteritems()}
  elif isinstance(string, list):
    return [byteify(element) for element in string]
  elif isinstance(string, unicode):
    return string.encode('utf-8')
  else:
    return string

def getProtectedProperty(document, select):
  """getProtectedProperty is a security-aware substitution for builtin `getattr`

  It resolves Properties on Products (visible via Zope Formulator), which are
  accessible as ordinary attributes as well, by following security rules.

  See https://lab.nexedi.com/nexedi/erp5/blob/master/product/ERP5Form/ListBox.py#L2293
  """
  try:
    #see https://lab.nexedi.com/nexedi/erp5/blob/master/product/ERP5Form/ListBox.py#L2293
    try:
      select = select[select.rindex('.') + 1:]
    except ValueError:
      pass

    return document.getProperty(select, d=None)
  except (ConflictError, RuntimeError):
    raise
  except:
    return None

def selectKwargsForCallable(func, initial_kwargs, kwargs_dict):
  """Create a copy of `kwargs_dict` with only items suitable for `func`.

  In case the function cannot state required arguments it throws an AttributeError.
  """
  if not hasattr(func, 'params'):
    return initial_kwargs

  func_param_list = [func_param.strip() for func_param in func.params().split(",")]
  func_param_name_list = [func_param if '=' not in func_param else func_param.split('=')[0]
                          for func_param in func_param_list if '*' not in func_param]
  for func_param_name in func_param_name_list:
    if func_param_name in kwargs_dict and func_param_name not in initial_kwargs:
      initial_kwargs[func_param_name] = kwargs_dict.get(func_param_name)
  # MIDDLE-DANGEROUS!
  # In case of reports (later even exports) substitute None for unknown
  # parameters. We suppose Python syntax for parameters!
  # What we do here is literally putting every form field from `kwargs_dict`
  # into search method parameters - this is later put back into `kwargs_dict`
  # this way we can mimic synchronous rendering when all form field values
  # were available in `kwargs_dict`. It is obviously wrong behaviour.
  for func_param in func_param_list:
    if "*" in func_param:
      continue
    if "=" in func_param:
      continue
    # now we have only mandatory parameters
    func_param = func_param.strip()
    if func_param not in initial_kwargs:
      initial_kwargs[func_param] = None
  return initial_kwargs


def getUidAndAccessorForAnything(search_result, result_index, traversed_document):
  """Return unique ID, unique URL, getter and hasser for any combination of `search_result` and `index`.

  You want to use this method when you need a unique reference to random object in iterable (for example
  result of list_method or stat_method). This will give you UID and URL for identification within JIO and
  accessors to test/access object's properties.

  Usage::

  for i, random_object in enumerate(unknown_iterable):
    uid, url, getter, hasser = object_ids_and_access(random_object, i)
    if hasser(random_object, "linkable"):
      result[uid] = {'url': portal.abolute_url() + url}
    value = getter(random_object, "value")
  """
  if hasattr(search_result, "getObject"):
    # search_result = search_result.getObject()
    contents_uid = search_result.uid
    # every document indexed in catalog has to have relativeUrl
    contents_relative_url = getRealRelativeUrl(search_result)
    # get property in secure way from documents
    search_property_getter = getProtectedProperty
    def search_property_hasser (doc, attr):
      """Brains cannot access Properties - they use permissioned getters."""
      try:
        return doc.hasProperty(attr)
      except (AttributeError, Unauthorized) as e:
        log('Cannot state ownership of property "{}" on {!s} because of "{!s}"'.format(
          attr, doc, e))
        return False
  elif hasattr(search_result, "aq_self"):
    # Zope products have at least ID thus we work with that
    contents_uid = search_result.uid
    # either we got a document with relativeUrl or we got product and use ID
    contents_relative_url = getRealRelativeUrl(search_result) or search_result.getId()
    # documents and products have the same way of accessing properties
    search_property_getter = getProtectedProperty
    search_property_hasser = lambda doc, attr: doc.hasProperty(attr)
  else:
    # In case of reports the `search_result` can be list of
    # PythonScripts.standard._Object - a reimplementation of plain dictionary

    # means we are iterating over plain objects
    # list_method must be defined because POPOs can return only that
    contents_uid = "{}#{:d}".format(list_method, result_index)
    # JIO requires every item to have _links.self.href so it can construct
    # links to the document. Here we have a object in RAM (which should
    # never happen!) thus we provide temporary UID
    contents_relative_url = "{}/{}".format(traversed_document.getRelativeUrl(), contents_uid)
    # property getter must be simple __getattr__ implementation
    search_property_getter = lambda obj, attr: getattr(obj, attr, None)
    search_property_hasser = lambda obj, attr: hasattr(obj, attr)

  return contents_uid, contents_relative_url, search_property_getter, search_property_hasser


def getAttrFromAnything(search_result, select, search_property_getter, search_property_hasser, kwargs):
  """Given `search_result` extract value named `select` using helper getter/hasser.

  :param search_result: any dict-like object (usually dict or Brain or Document)
  :param select: field name (can represent actual attributes, Properties or even Scripts)
  :param kwargs: available arguments for possible callables hidden under `select`
  """

  # if the variable does not have a field template we need to find its
  # value by resolving value in the correct order. The code is copy&pasted
  # from ListBoxRendererLine.getValueList because it is universal
  contents_value = None

  if not isinstance(select, (str, unicode)) or len(select) == 0:
    log('There is an invalid column name "{!s}"!'.format(select), level=200)
    return None

  if "." in select:
    select = select[select.rindex('.') + 1:]

  # prepare accessor/getter name because this must be the first tried possibility
  # getter is preferred way how to obtain properties - property itself is the second
  if not select.startswith('get') and select[0] not in string.ascii_uppercase:
    # maybe a hidden getter (variable accessible by a getter)
    accessor_name = 'get' + UpperCase(select)
  else:
    # or obvious getter (starts with "get" or Capital letter - Script)
    accessor_name = select

  # 1. resolve attribute on a raw object (all wrappers removed) using
  # lowest-level secure getattr method given object type
  raw_search_result = search_result
  if hasattr(search_result, 'aq_base'):
    raw_search_result = search_result.aq_base
  # BUT! only if there is no accessor (because that is the prefered way)
  if search_property_hasser(raw_search_result, select) and not hasattr(raw_search_result, accessor_name):
    contents_value = search_property_getter(raw_search_result, select)

  # 2. use the fact that wrappers (brain or acquisition wrapper) use
  # permissioned getters
  unwrapped_search_result = search_result
  if hasattr(search_result, 'aq_self'):
    unwrapped_search_result = search_result.aq_self

  if contents_value is None:
    # again we check on a unwrapped object to avoid acquisition resolution
    # which would certainly find something which we don't want
    try:
      if hasattr(raw_search_result, accessor_name) and callable(getattr(search_result, accessor_name)):
        # test on raw object but get the actual accessor using wrapper and acquisition
        # do not call it here - it will be done later in generic call part
        contents_value = getattr(search_result, accessor_name)
    except (AttributeError, KeyError, Unauthorized) as error:
      log("Could not evaluate {} nor {} on {} with error {!s}".format(
        select, accessor_name, search_result, error), level=100)  # WARNING

  if contents_value is None and search_property_hasser(search_result, select):
    # maybe it is just a attribute
    contents_value = search_property_getter(search_result, select)

  if contents_value is None:
    try:
      contents_value = getattr(search_result, select, None)
    except (Unauthorized, AttributeError, KeyError) as error:
      log("Cannot resolve {} on {!s} because {!s}".format(
        select, raw_search_result, error), level=100)

  if callable(contents_value):
    has_mandatory_param = False
    has_brain_param = False
    if hasattr(contents_value, "params"):
      has_mandatory_param = any(map(lambda param: '=' not in param and '*' not in param,
                                    contents_value.params().split(","))) \
                            if contents_value.params() \
                            else False # because any([]) == True
      has_brain_param = "brain" in contents_value.params()
    try:
      if has_mandatory_param:
        contents_value = contents_value(search_result)
      elif has_brain_param:
        contents_value = contents_value(brain=search_result)
      else:
        contents_value = contents_value()
    except (AttributeError, KeyError, Unauthorized) as error:
      log("Could not evaluate {} on {} with error {!s}".format(
        contents_value, search_result, error), level=100)  # WARNING

  # make resulting value JSON serializable
  if contents_value is not None:
    if same_type(contents_value, DateTime()):
      # Serialize DateTime
      contents_value = contents_value.rfc822()
    # XXX Kato: what exactly should the later mean?
    elif isinstance(contents_value, datetime.date):
      contents_value = formatdate(time.mktime(contents_value.timetuple()))
    elif hasattr(contents_value, 'translate'):
      contents_value = "%s" % contents_value

  return contents_value


url_template_dict = {
  "form_action": "%(traversed_document_url)s/%(action_id)s",
  "traverse_generator": "%(root_url)s/%(script_id)s?mode=traverse" + \
                       "&relative_url=%(relative_url)s&view=%(view)s",
  "traverse_template": "%(root_url)s/%(script_id)s?mode=traverse" + \
                       "{&relative_url,view}",
  "search_template": "%(root_url)s/%(script_id)s?mode=search" + \
                     "{&query,select_list*,limit*,sort_on*,local_roles*}",
  "worklist_template": "%(root_url)s/%(script_id)s?mode=worklist",
  "custom_search_template": "%(root_url)s/%(script_id)s?mode=search" + \
                     "&relative_url=%(relative_url)s" \
                     "&form_relative_url=%(form_relative_url)s" \
                     "&list_method=%(list_method)s" \
                     "&default_param_json=%(default_param_json)s" \
                     "{&query,select_list*,limit*,sort_on*,local_roles*}",
  "custom_search_template_no_editable": "%(root_url)s/%(script_id)s?mode=search" + \
                     "&relative_url=%(relative_url)s" \
                     "&list_method=%(list_method)s" \
                     "&default_param_json=%(default_param_json)s" \
                     "{&query,select_list*,limit*,sort_on*,local_roles*}",
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

def getFormRelativeUrl(form):
  return portal.portal_catalog(
    portal_type="ERP5 Form",
    uid=form.getUid(),
    id=form.getId(),
    limit=1,
    select_dict={'relative_url': None}
  )[0].relative_url

def getFieldDefault(traversed_document, field, key, value=None):
  # REQUEST.get(field.id, field.get_value("default"))
  result = traversed_document.Field_getDefaultValue(field, key, value, REQUEST)
  if getattr(result, 'translate', None) is not None:
    result = "%s" % result
  return result


def renderField(traversed_document, field, form, value=None, meta_type=None, key=None, key_prefix=None, selection_params=None):
  """Extract important field's attributes into `result` dictionary."""

  if selection_params is None:
    selection_params = {}

  # some TALES expressions are using Base_getRelatedObjectParameter which requires that
  previous_request_field = REQUEST.other.pop('field_id', None)
  REQUEST.other['field_id'] = field.id

  if meta_type is None:
    meta_type = field.meta_type
  if key is None:
    key = field.generate_field_key(key_prefix=key_prefix)

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
    result.update({
      "required": field.get_value("required") if field.has_value("required") else None,
      "default": getFieldDefault(traversed_document, field, result["key"], value),
    })

  if meta_type == "ProxyField":
    return renderField(traversed_document, field, form, value,
                       meta_type=field.getRecursiveTemplateField().meta_type,
                       key=key, key_prefix=key_prefix,
                       selection_params=selection_params)

  if meta_type in ("ListField", "RadioField", "ParallelListField", "MultiListField"):
    result.update({
      # XXX Message can not be converted to json as is
      "items": field.get_value("items"),
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
    date_value = getFieldDefault(traversed_document, field, result["key"], value)
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
    if portal_type_list:
      portal_type_list = [x[0] for x in portal_type_list]
      translated_portal_type = [Base_translateString(x) for x in portal_type_list]
      # ported from Base_jumpToRelatedDocument\n
      base_category = field.get_value('base_category')
      kw = {}
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
    query = url_template_dict["jio_search_template"] % {
      "query": make_query({"query": sql_catalog.buildQuery(
        {"portal_type": portal_type_list}
      ).asSearchTextExpression(sql_catalog)})
    }
    title = field.get_value("title")
    column_list = field.get_value("columns")
    proxy_listbox_ids = field.get_value("proxy_listbox_ids")

    if len(proxy_listbox_ids):
      listbox_ids = proxy_listbox_ids
    else:
      listbox_ids = [('Base_viewRelatedObjectListBase/listbox','default')]
    listbox = {}

    for (listbox_path, listbox_name) in listbox_ids:
      (listbox_form_name, listbox_field_name) = listbox_path.split('/', 2)
      # do not override "global" `form`
      rel_form = getattr(context, listbox_form_name)
      # find listbox field
      listbox_form_field = filter(lambda f: f.getId() == listbox_field_name, rel_form.get_fields())[0]
      rel_cache = {'form_id': REQUEST.get('form_id', MARKER), 'field_id': REQUEST.get('field_id', MARKER)}
      REQUEST.set('form_id', rel_form.id)
      REQUEST.set('field_id', listbox_form_field.id)

      # get original definition
      subfield = renderField(context, listbox_form_field, rel_form)
      # overwrite, like Base_getRelatedObjectParameter does
      if subfield["portal_type"] == []:
        subfield["portal_type"] = field.get_value('portal_type')
      subfield["query"] = url_template_dict["jio_search_template"] % {
        "query": make_query({"query": sql_catalog.buildQuery(
          dict(portal_type = [x[-1] for x in subfield["portal_type"]],
            **subfield["default_params"]), ignore_unknown_columns=True
       ).asSearchTextExpression(sql_catalog)})
      }
      # Kato: why?
      if "list_method_template" in subfield:
        del subfield["list_method_template"]
      subfield["list_method"] = "portal_catalog"
      subfield["title"] = Base_translateString(title)
      #set default listbox's column list to relation's column list
      if listbox_form_name == 'Base_viewRelatedObjectListBase' and len(column_list) > 0:
        subfield["column_list"] = []
        for tmp_column in column_list:
          subfield["column_list"].append((tmp_column[0], Base_translateString(tmp_column[1])))
      listbox[Base_translateString(listbox_name)] = subfield

      for key in rel_cache:
        if rel_cache[key] is not MARKER:
          REQUEST.set(key, rel_cache[key])


    result.update({
      "url": relative_url,
      "translated_portal_types": translated_portal_type,
      "portal_types": portal_type_list,
      "query": query,
      "catalog_index": field.get_value('catalog_index'),
      "allow_jump": field.get_value('allow_jump'),
      "allow_creation": field.get_value('allow_creation'),
      "proxy_listbox_ids_len": len(proxy_listbox_ids),
      "listbox": listbox,
    })

    if not isinstance(result["default"], list):
      result["default"] = [result["default"], ]

    result.update({
      "relation_field_id": traversed_document.Field_getSubFieldKeyDict(field, "relation", key=result["key"]),
      "relation_item_key": traversed_document.Field_getSubFieldKeyDict(field, "item", key=result["key"]),
      "relation_item_relative_url": [jump_reference.getRelativeUrl() for jump_reference in jump_reference_list]
    })
    return result

  if meta_type in ("CheckBoxField", "MultiCheckBoxField"):
    if meta_type == "MultiCheckBoxField":
      result["items"] = field.get_value("items"),
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
    """Display list of objects with optional search/sort capabilities on columns from catalog."""
    _translate = Base_translateString

    column_list = [(name, _translate(title)) for name, title in field.get_value("columns")]
    all_column_list = [(name, _translate(title)) for name, title in field.get_value("all_columns")]
    editable_column_list = [(name, _translate(title)) for name, title in field.get_value("editable_columns")]
    catalog_column_list = [(name, title)
                           for name, title in OrderedDict(column_list + all_column_list).items()
                           if sql_catalog.isValidColumn(name)]

    # try to get specified searchable columns and fail back to all searchable columns
    search_column_list = [(name, _translate(title))
                          for name, title in field.get_value("search_columns")
                          if sql_catalog.isValidColumn(name)] or catalog_column_list

    # try to get specified sortable columns and fail back to searchable fields
    sort_column_list = [(name, _translate(title))
                        for name, title in field.get_value("sort_columns")
                        if sql_catalog.isValidColumn(name)] or search_column_list

    # requirement: get only sortable/searchable columns which are already displayed in listbox
    # see https://lab.nexedi.com/nexedi/erp5/blob/HEAD/product/ERP5Form/ListBox.py#L1004
    # implemented in javascript in the end
    # see https://lab.nexedi.com/nexedi/erp5/blob/master/bt5/erp5_web_renderjs_ui/PathTemplateItem/web_page_module/rjs_gadget_erp5_listbox_js.js#L163

    portal_types = field.get_value('portal_types')
    default_params = dict(field.get_value('default_params'))
    default_params['ignore_unknown_columns'] = True
    if selection_params is not None:
      default_params.update(selection_params)
    # How to implement pagination?
    # default_params.update(REQUEST.form)
    lines = field.get_value('lines')
    list_method_query_dict = dict(
      portal_type=[x[1] for x in portal_types], **default_params
    )
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
      # Now if the list_method does not specify **kwargs we need to remove
      # unwanted parameters like "portal_type" which is everywhere
      if hasattr(list_method, 'params') and "**" not in list_method.params():
        _param_key_list = tuple(list_method_query_dict.keys()) # copy the keys
        for param_key in _param_key_list:
          if param_key not in list_method.params():  # we search in raw string
            del list_method_query_dict[param_key]    # but it is enough

    if (editable_column_list):
      list_method_custom = url_template_dict["custom_search_template"] % {
        "root_url": site_root.absolute_url(),
        "script_id": script.id,
        "relative_url": traversed_document.getRelativeUrl().replace("/", "%2F"),
        "form_relative_url": "%s/%s" % (getFormRelativeUrl(form), field.id),
        "list_method": list_method_name,
        "default_param_json": urlsafe_b64encode(json.dumps(list_method_query_dict))
      }
      list_method_query_dict = {}
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
        "default_param_json": urlsafe_b64encode(json.dumps(list_method_query_dict))
      }
      list_method_query_dict = {}

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
      "portal_type": portal_types,
      "lines": lines,
      "default_params": default_params,
      "list_method": list_method_name,
      "query": url_template_dict["jio_search_template"] % {
        "query": make_query({
          "query": sql_catalog.buildQuery(
            list_method_query_dict,
            ignore_unknown_columns=True).asSearchTextExpression(sql_catalog)})}
    })
    if (list_method_custom is not None):
      result["list_method_template"] = list_method_custom
    return result

  if meta_type == "FormBox":
    embedded_document = {
      '_links': {},
      '_actions': {},
    }

    # FormBox might have own context if 'context_method_id' is defined
    formbox_context = traversed_document
    if field.get_value('context_method_id'):
      # harness acquisition and call the method right away
      formbox_context = getattr(traversed_document, field.get_value('context_method_id'))()
      embedded_document['_debug'] = "Different context"

    embeded_form = getattr(formbox_context, field.get_value('formbox_target_id'))
    # renderForm mutates `embedded_document` therefor no return/assignment
    renderForm(formbox_context, embeded_form, embedded_document, key_prefix=key)
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


def renderForm(traversed_document, form, response_dict, key_prefix=None, selection_params=None):
  """
  :param selection_params: holds parameters to construct ERP5Form.Selection instance
      for underlaying ListBox - since we do not use selections in RenderJS UI
      we mitigate the functionality here by overriding ListBox's own values
      for columns, editable columns, and sort with those found in `selection_params`
  """
  previous_request_other = {
    'form_id': REQUEST.other.pop('form_id', None),
    'here': REQUEST.other.pop('here', None)
  }
  REQUEST.set('here', traversed_document)
  REQUEST.set('form_id', form.id)
  field_errors = REQUEST.get('field_errors', {})

  #hardcoded
  include_action = True
  if form.pt == 'form_dialog':
    action_to_call = "Base_callDialogMethod"
  else:
    action_to_call = form.action
  if (action_to_call == 'Base_edit') and (not portal.portal_membership.checkPermission('Modify portal content', traversed_document)):
    # prevent allowing editing if user doesn't have permission
    include_action = False

  if (include_action):
    # Form action
    response_dict['_actions'] = {
      'put': {
        "href": url_template_dict["form_action"] % {
          "traversed_document_url": site_root.absolute_url() + "/" + traversed_document.getRelativeUrl(),
          "action_id": action_to_call
        },
        "action": form.action,
        "method": form.method,
      }
    }
  # Form traversed_document
  response_dict['_links']['traversed_document'] = {
    "href": default_document_uri_template % {
      "root_url": site_root.absolute_url(),
      "relative_url": traversed_document.getRelativeUrl(),
      "script_id": script.id
    },
    "name": traversed_document.getRelativeUrl(),
    "title": traversed_document.getTitle()
  }

  form_relative_url = getFormRelativeUrl(form)
  response_dict['_links']['form_definition'] = {
#     "href": default_document_uri_template % {
#       "root_url": site_root.absolute_url(),
#       "script_id": script.id,
#       "relative_url": getFormRelativeUrl(form)
#     },
    "href": default_document_uri_template % {
      "relative_url": form_relative_url
    },
    'name': form.id
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
        response_dict[field.id] = renderField(traversed_document, field, form, key_prefix=key_prefix, selection_params=selection_params)
        if field_errors.has_key(field.id):
          response_dict[field.id]["error_text"] = field_errors[field.id].error_text
      except AttributeError:
        # Do not crash if field configuration is wrong.
        pass

  response_dict["form_id"] = {
    "type": "StringField",
    "key": "form_id",
    "default": form.id,
    "editable": 0,
    "css_class": "",
    "hidden": 1,
    "description": "",
    "title": "form_id",
    "required": 1,
  }

  if (form.pt == 'report_view'):
    report_item_list = []
    report_result_list = []
    for field in form.get_fields():
      if field.getRecursiveTemplateField().meta_type == 'ReportBox':
        report_item_list.extend(field.render())
    j = 0
    for report_item in report_item_list:
      report_context = report_item.getObject(portal)
      report_prefix = 'x%s' % j
      j += 1
      report_title = report_item.getTitle()
      # report_class = "report_title_level_%s" % report_item.getLevel()
      report_form = report_item.getFormId()
      report_result = {'_links': {}}
      renderForm(traversed_document, getattr(report_context, report_item.getFormId()),
                 report_result, key_prefix=report_prefix,
                 selection_params=report_item.selection_params)
      report_result_list.append(report_result)

    response_dict['report_section_list'] = report_result_list

# XXX form action update, etc
def renderRawField(field):
  meta_type = field.meta_type

  return {
    "meta_type": field.meta_type
  }


  if meta_type == "MethodField":
    result = {
      "meta_type": field.meta_type
    }
  else:
    result = {
      "meta_type": field.meta_type,
      "_values": field.values,
      # XXX TALES expression is not JSON serializable by default
      # "_tales": field.tales
      "_overrides": field.overrides
    }
  if meta_type == "ProxyField":
    result['_delegated_list'] = field.delegated_list
#     try:
#       result['_delegated_list'].pop('list_method')
#     except KeyError:
#       pass

  # XXX ListMethod is not JSON serialized by default
  try:
    result['_values'].pop('list_method')
  except KeyError:
    pass
  try:
    result['_overrides'].pop('list_method')
  except KeyError:
    pass
  return result


def renderFormDefinition(form, response_dict):
  group_list = []
  for group in form.Form_getGroupTitleAndId():

    if group['gid'].find('hidden') < 0:
      field_list = []

      for field in form.get_fields_in_group(group['goid'], include_disabled=1):
        field_list.append((field.id, renderRawField(field)))

      group_list.append((group['gid'], field_list))
  response_dict["group_list"] = group_list
  response_dict["title"] = Base_translateString(form.getTitle())
  response_dict["pt"] = form.pt
  response_dict["action"] = form.action


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

context.Base_prepareCorsResponse(RESPONSE=response)

# Check if traversed_document is the site_root
if relative_url:
  temp_traversed_document = site_root.restrictedTraverse(relative_url, None)
  if (temp_traversed_document is None):
    response.setStatus(404)
    return ""
else:
  temp_traversed_document = context

temp_is_site_root = (temp_traversed_document.getPath() == site_root.getPath())
temp_is_portal = (temp_traversed_document.getPath() == portal.getPath())

def calculateHateoas(is_portal=None, is_site_root=None, traversed_document=None, REQUEST=None,
                     response=None, view=None, mode=None, query=None,
                     select_list=None, limit=None, form=None,
                     relative_url=None, restricted=None, list_method=None,
                     default_param_json=None, form_relative_url=None):

  if relative_url:
    try:
      traversed_document = site_root.restrictedTraverse(str(relative_url))
      view = str(view)
      is_site_root = False
    except:
      raise NotImplementedError(relative_url)
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
  }
  
  
  if (restricted == 1) and (portal.portal_membership.isAnonymousUser()):
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
  
  elif mime_type != traversed_document.Base_handleAcceptHeader([mime_type]):
    response.setStatus(406)
    return ""
  
  
  elif (mode == 'root') or (mode == 'traverse'):
    #################################################
    # Raw document
    #################################################
    if (REQUEST is not None) and (REQUEST.other['method'] != "GET"):
      response.setStatus(405)
      return ""
    # Default properties shared by all ERP5 Document and Site
    action_dict = {}
  #   result_dict['_relative_url'] = traversed_document.getRelativeUrl()
    result_dict['title'] = traversed_document.getTitle()
  
    # Add a link to the portal type if possible
    if not is_portal:
      result_dict['_links']['type'] = {
        "href": default_document_uri_template % {
          "root_url": site_root.absolute_url(),
          "relative_url": portal.portal_types[traversed_document.getPortalType()]\
                            .getRelativeUrl(), 
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
  
    # XXX Loop on form rendering
    erp5_action_dict = portal.Base_filterDuplicateActions(
      portal.portal_actions.listFilteredActionsFor(traversed_document))
  
    embedded_url = None
    # XXX See ERP5Type.getDefaultViewFor
    for erp5_action_key in erp5_action_dict.keys():
      erp5_action_list = []
      for view_action in erp5_action_dict[erp5_action_key]:
        # Action condition is probably checked in Base_filterDuplicateActions
        erp5_action_list.append({
          'href': '%s' % view_action['url'],
          'name': view_action['id'],
          'icon': view_action['icon'],
          'title': Base_translateString(view_action['title']) \
            if erp5_action_key != "workflow" else view_action['title'],
        })
        # Try to embed the form in the result
        if (view == view_action['id']):
          embedded_url = '%s' % view_action['url']

        global_action_type = ("view", "workflow", "object_new_content_action", 
                              "object_clone_action", "object_delete_action")
        if (erp5_action_key == view_action_type or
            erp5_action_key in global_action_type or
            "_jio" in erp5_action_key):
          erp5_action_list[-1]['href'] = url_template_dict["traverse_generator"] % {
                "root_url": site_root.absolute_url(),
                "script_id": script.id,
                "relative_url": traversed_document.getRelativeUrl().replace("/", "%2F"),
                "view": erp5_action_list[-1]['name']
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
          
        # XXX Put a prefix to prevent conflict
        result_dict['_links']["action_" + erp5_action_key] = erp5_action_list
  
  #   for view_action in erp5_action_dict.get('object_view', []):
  #     traversed_document.log(view_action)
  #     # XXX Check the action condition
  # #     if (view is None) or (view != view_action['name']):
  #     object_view_list.append({
  #       'href': '%s' % view_action['url'],
  #       'name': view_action['name']
  #     })
  
  
  #   if (renderer_form is not None):
  #     traversed_document_property_dict, renderer_form_json = traversed_document.Base_renderFormAsSomething(renderer_form)
  #     result_dict['_embedded'] = {
  #       'object_view': renderer_form_json
  #     }
  #     result_dict.update(traversed_document_property_dict)
  
    # XXX XXX XXX XXX
    if (embedded_url is not None):
      # XXX Try to fetch the form in the traversed_document of the document
      # Of course, this code will completely crash in many cases (page template
      # instead of form, unexpected action TALES expression). Happy debugging.
      # renderer_form_relative_url = view_action['url'][len(portal.absolute_url()):]
      form_id = embedded_url.split('?', 1)[0].split("/")[-1]
      # renderer_form = traversed_document.restrictedTraverse(form_id, None)
      # XXX Proxy field are not correctly handled in traversed_document of web site
      renderer_form = getattr(traversed_document, form_id)
  #     traversed_document.log(form_id)
      if (renderer_form is not None):
        embedded_dict = {
          '_links': {
            'self': {
              'href': embedded_url
            }
          }
        }
        # Put all query parameters (?reset:int=1&workflow_action=start_action) in request to mimic usual form display
        query_split = embedded_url.split('?', 1)
        if len(query_split) == 2:
          for query_parameter in query_split[1].split("&"):
            query_key, query_value = query_parameter.split("=")
            REQUEST.set(query_key, query_value)
  
        renderForm(traversed_document, renderer_form, embedded_dict)
        result_dict['_embedded'] = {
          '_view': embedded_dict
          # embedded_action_key: embedded_dict
        }
  #       result_dict['_links']["_view"] = {"href": embedded_url}
  
        # Include properties in document JSON
        # XXX Extract from renderer form?
        """
        for group in renderer_form.Form_getGroupTitleAndId():
          for field in renderer_form.get_fields_in_group(group['goid']):
            field_id = field.id
  #           traversed_document.log(field_id)
            if field_id.startswith('my_'):
              property_name = field_id[len('my_'):]
  #             traversed_document.log(property_name)
              property_value = traversed_document.getProperty(property_name, d=None)
              if (property_value is not None):
                if same_type(property_value, DateTime()):
                  # Serialize DateTime
                  property_value = property_value.rfc822()
                result_dict[property_name] = property_value 
                """
  
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
      if traversed_document_portal_type == "ERP5 Form":
        renderFormDefinition(traversed_document, result_dict)
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
    #  list_method: objectValues                      (Script providing listing)
    #  default_param_json: <base64 encoded JSON>      (Additional search params)
    #  query: <str>                                   (term for fulltext search)
    #  select_list: ['int_index', 'id', 'title', ...] (column names to select)
    #  limit: [15, 16]                                (begin_index, num_records)
    #  local_roles: TODO
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
    #################################################
    if REQUEST.other['method'] != "GET":
      response.setStatus(405)
      return ""

    # set 'here' for field rendering which contain TALES expressions
    REQUEST.set('here', traversed_document)

    # in case we have custom list method
    catalog_kw = {}

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
        "limit": limit,
        "sort_on": ()  # default is an empty tuple
      }
      if default_param_json is not None:
        catalog_kw.update(byteify(json.loads(urlsafe_b64decode(default_param_json))))
      if query:
        catalog_kw["full_text"] = query
      if sort_on is not None:
        def parseSortOn(raw_string):
          """Turn JSON serialized array into a tuple (col_name, order)."""
          sort_col, sort_order = json.loads(raw_string)
          sort_col, sort_order = byteify(sort_col), byteify(sort_order)
          # JIO keeps sort order as whole word 'ascending' resp. 'descending'
          if sort_order.lower().startswith("asc"):
            sort_order = "ASC"
          elif sort_order.lower().startswith("desc"):
            sort_order = "DESC"
          else:
            # should raise an ValueError instead
            log('Wrong sort order "{}" in {}! It must start with "asc" or "desc"'.format(sort_order, form_relative_url),
                        level=200)  # error
          return (sort_col, sort_order)

        if isinstance(sort_on, list):
          # sort_on argument is always a list of tuples(col_name, order)
          catalog_kw['sort_on'] = list(map(parseSortOn, sort_on))
        else:
          catalog_kw['sort_on'] = [parseSortOn(sort_on), ]

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

    # form field issuing this search
    source_field = portal.restrictedTraverse(form_relative_url) if form_relative_url else None

    # extract form field definition into `editable_field_dict`
    editable_field_dict = {}
    listbox_form = None
    listbox_field_id = None
    source_field_meta_type = source_field.meta_type if source_field is not None else ""
    if source_field_meta_type == "ProxyField":
      source_field_meta_type = source_field.getRecursiveTemplateField().meta_type

    if source_field is not None and source_field_meta_type == "ListBox":
      listbox_field_id = source_field.id
      # XXX Proxy field are not correctly handled in traversed_document of web site
      listbox_form = getattr(traversed_document, source_field.aq_parent.id)

      # field TALES expression evaluated by Base_getRelatedObjectParameter requires that
      REQUEST.other['form_id'] = listbox_form.id

      for select in select_list:
        # See Listbox.py getValueList --> getEditableField & getColumnAliasList method
        # In short: there are Form Field definitions which names start with
        # matching ListBox name - those are template fields to be rendered in
        # cells with actual values defined by row and column
        field_name = "{}_{}".format(listbox_field_id, select.replace(".", "_"))
        if listbox_form.has_field(field_name, include_disabled=1):
          editable_field_dict[select] = listbox_form.get_field(field_name, include_disabled=1)

    # handle the case when list-scripts are ignoring `limit` - paginate for them
    if limit is not None and isinstance(limit, (tuple, list)):
      start, num_items = map(int, limit)
      if len(search_result_iterable) <= num_items:
        # the limit was most likely taken into account thus we don't need to slice
        start, num_items = 0, len(search_result_iterable)
    else:
      start, num_items = 0, len(search_result_iterable)

    contents_list = []  # resolved fields from the search result
    result_dict.update({
      '_query': query,
      '_local_roles': local_roles,
      '_limit': limit,
      '_select_list': select_list,
      '_embedded': {}
    })
    # now fill in `contents_list` with actual information
    # beware that search_result_iterable can hide anything inside!
    for result_index, search_result in enumerate(search_result_iterable):
      # skip documents out of `limit`
      if result_index < start:
        continue
      if result_index >= start + num_items:
        break

      # we can render fields which need 'here' to be set to currently rendered document
      #REQUEST.set('here', search_result)
      contents_item = {}
      contents_uid, contents_relative_url, property_getter, property_hasser = \
        getUidAndAccessorForAnything(search_result, result_index, traversed_document)

      # _links.self.href is mandatory for JIO so it can create reference to the
      # (listbox) item alone
      contents_item['_links'] = {
        'self': {
          "href": default_document_uri_template % {
            "root_url": site_root.absolute_url(),
            "relative_url": contents_relative_url,
            "script_id": script.id
          },
        },
      }

      # ERP5 stores&send the list of editable elements in a hidden field called
      # only database results can be editable so it belongs here
      if editable_field_dict and listbox_field_id:
        contents_item['listbox_uid:list'] = {
          'key': "%s_uid:list" % listbox_field_id,
          'value': contents_uid
        }

      for select in select_list:
        if editable_field_dict.has_key(select):
          # cell has a Form Field template thus render it using the field
          # fields are nice because they are standard
          REQUEST.set('cell', search_result)
          # if default value is given by evaluating Tales expression then we only
          # put "cell" to request (expected by tales) and let the field evaluate
          if getattr(editable_field_dict[select].tales, "default", "") == "":
            # if there is no tales expr (or is empty) we extract the value from search result
            default_field_value = getAttrFromAnything(search_result, select, property_getter, property_hasser, {})

          contents_item[select] = renderField(
            traversed_document,
            editable_field_dict[select],
            listbox_form,
            value=default_field_value,
            key='field_%s_%s' % (editable_field_dict[select].id, contents_uid))

          REQUEST.other.pop('cell', None)
        else:
          # most of the complicated magic happens here - we need to resolve field names
          # given search_result. This name can unfortunately mean almost anything from
          # a key name to Python Script with variable number of input parameters.
          contents_item[select] = getAttrFromAnything(search_result, select, property_getter, property_hasser, {'brain': search_result})
      # endfor select
      contents_list.append(contents_item)
    result_dict['_embedded']['contents'] = contents_list

    return result_dict

  elif mode == 'form':
    #################################################
    # Calculate form value
    #################################################
    if REQUEST.other['method'] != "POST":
      response.setStatus(405)
      return ""
  
    renderForm(traversed_document, form, result_dict)
  
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
            worklist_module_id = portal.getDefaultModuleId(portal_type, default=None, only_visible=True)
          elif (worklist_module_id != portal.getDefaultModuleId(portal_type, default=None, only_visible=True)):
            worklist_module_id = None
          if worklist_module_id is None:
            break

        if (worklist_module_id is not None):
          worklist_dict['module'] = default_document_uri_template % {
            "relative_url": worklist_module_id
          }
      work_list.append(worklist_dict)

    result_dict["worklist"] = work_list

  else:
    raise NotImplementedError("Unsupported mode %s" % mode)
  
  return result_dict

response.setHeader('Content-Type', mime_type)
hateoas = calculateHateoas(is_portal=temp_is_portal, is_site_root=temp_is_site_root,
                           traversed_document=temp_traversed_document,
                           relative_url=relative_url,
                           REQUEST=REQUEST, response=response, view=view, mode=mode,
                           query=query, select_list=select_list, limit=limit, form=form,
                           restricted=restricted, list_method=list_method,
                           default_param_json=default_param_json,
                           form_relative_url=form_relative_url)
if hateoas == "":
  return hateoas
else:
  return json.dumps(hateoas, indent=2)
