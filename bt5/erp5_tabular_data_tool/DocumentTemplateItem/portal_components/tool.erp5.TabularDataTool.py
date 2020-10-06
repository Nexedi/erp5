from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Tool.BaseTool import BaseTool
import pandas as pd

MARKER = object()
DEFAULT_FILL_STRING = ''
DEFAULT_FILL_NUMBER = 0.0
DEFAULT_FILL_UID = -1

class TabularDataTool(BaseTool):
  """
  Tabular Data Tool is a Tool to handle tabular data (2-dimentional table data) in erp5.
  The tabular data type is currently a plain pandas DataFrame. It is intended to
  use with ERP5 Reports to create spread sheets (ODS/Excel).

  With Tabular Data Tool, we can do those things on reporting:
  - transform dict-list, portal-catalog-result and document-list into a tabular data
  - joining/grouping/sorting the tabular data
  - using vectorizing function to optimise time consuming reports
  """
  id = 'portal_tabular'
  title = 'Tabular Datas'
  meta_type = 'ERP5 Tabular Data Tool'
  portal_type = 'Tabular Data Tool'
  allowed_types = ()


  # Declarative Security
  security = ClassSecurityInfo()

  # The empty DataFrame marker
  def _createEmptyDataFrame(self):
    return pd.DataFrame()

  security.declareProtected(Permissions.AccessContentsInformation, 'fillna')
  def fillna(self, tabular, fillna_on_string=MARKER, fillna_on_number=MARKER, fillna_on_uid=MARKER):
    """
    Fill NA/NaN values on the given tabular (a dataframe).

    Keyword arguments:
    tabular -- the dataframe to fill empty values
    fillna_on_string -- Fill given value for empty string
    fillna_on_number -- Fill given value for empty numbers (int or float)
    fillna_on_uid -- Fill given value for empty uid, which overrides fillna_on_numbers for uid
    """
    if tabular is None:
      return tabular
    string_filler = DEFAULT_FILL_STRING if fillna_on_string is MARKER else fillna_on_string
    number_filler = DEFAULT_FILL_NUMBER if fillna_on_number is MARKER else fillna_on_number
    uid_filler = DEFAULT_FILL_UID if fillna_on_uid is MARKER else fillna_on_uid
    fillna_setting_dict = {}
    string_column_list = tabular.select_dtypes(include=[object]).columns.tolist()
    string_none_column_list = []
    if fillna_on_string is None:
      # pandas.dataframe.fillna(None) raises error, so use .replace() instead
      string_none_column_list = string_column_list
      string_column_list = []
    number_column_list = tabular.select_dtypes(include=[int,float]).columns.tolist()
    uid_column_list = [column for column in tabular.columns.tolist() if column.endswith('_uid')]

    number_column_list = list(set(number_column_list) - set(uid_column_list))
    string_column_list = list(set(string_column_list) - set(uid_column_list))
    fillna_setting_dict.update(dict.fromkeys(string_column_list, string_filler))
    fillna_setting_dict.update(dict.fromkeys(number_column_list, number_filler))
    fillna_setting_dict.update(dict.fromkeys(uid_column_list, uid_filler))
    filled_tabular = tabular.fillna(value=fillna_setting_dict)
    if string_none_column_list:
      replace_dict = dict.fromkeys(string_none_column_list, {"":None})
      filled_tabular = filled_tabular.replace(replace_dict)
    return filled_tabular

  security.declareProtected(Permissions.AccessContentsInformation, 'getTabular')
  def getTabular(self, data_list,
                 fillna_on_string=MARKER,
                 fillna_on_number=MARKER,
                 fillna_on_uid=MARKER,
                 additional_property_name_list=MARKER):
    """
    Create a tabular from dict list with filling values for convenience in ERP5.
    Currently the tabular data type is pandas DataFrame.

    Keyword arguments:
    data_list -- A dict list or brain_list to convert it to dataframe
    fillna_on_string -- Fill given value for empty string
    fillna_on_numbers -- Fill given value for empty numbers (int or float)
    fillna_on_uid -- Fill given value for empty uid, which overrides fillna_on_numbers for uid
    additional_property_name_list -- Additional property name list of brain object
    """
    if data_list is None or len(data_list) == 0:
      return self._createEmptyDataFrame()
    df = None
    if isinstance(data_list[0], dict):
      df = pd.DataFrame.from_dict(data_list)

    # Expect Shared.ZRDB.Results
    elif getattr(data_list, 'dictionaries', None) is not None:
      if additional_property_name_list is not MARKER:
        new_data_dict_list = []
        for (data_, record_dict) in zip(data_list, data_list.dictionaries()):
          property_dict = self._getPropertyDict(data_, additional_property_name_list, False, False)
          property_dict.update(record_dict)
          new_data_dict_list.append(property_dict)
        df = self.getTabular(new_data_dict_list)
      else:
        df = self.getTabular(data_list.dictionaries())
    if df is not None:
      return self.fillna(df, fillna_on_string=fillna_on_string,
                         fillna_on_number=fillna_on_number,
                         fillna_on_uid=fillna_on_uid)
    raise ValueError("The type is not supported, {}".format(data_list))

  def _getPropertyDict(self, document, property_name_list, is_category_as_uid, add_category_title):
    portal_type = document.getPortalType()
    base_type = self.getPortalObject().portal_types[portal_type]
    base_category_list = base_type.getInstanceBaseCategoryList()
    if property_name_list is MARKER:
      property_name_list = list(base_type.getInstancePropertySet())
    else:
      # If property_name_list is explicitly passed, respect the name list in category
      base_category_list = list(set(base_category_list).intersection(set(property_name_list)))
    property_dict = {}
    for property_name in property_name_list:
      property_dict[property_name] = document.getProperty(property_name)
    for base_category_id in base_category_list:
      category_name = "{}_uid".format(base_category_id) if is_category_as_uid else base_category_id
      property_dict[category_name] = document.getProperty(category_name)
      if add_category_title:
        category_title = "{}_title".format(base_category_id)
        property_dict[category_title] = document.getProperty(category_title)
    return property_dict

  security.declareProtected(Permissions.AccessContentsInformation, 'getFromDocumentList')
  def getFromDocumentList(self, document_list,
                          property_name_list=MARKER,
                          fillna_on_string=MARKER,
                          fillna_on_number=MARKER,
                          fillna_on_uid=MARKER,
                          is_category_as_uid=True,
                          add_category_title=True):
    """
    Create tabular data from document list

    Keyword arguments:
    property_name_list -- Explict to specify the property name list of document
                          If not specified all properties and categories of the portal type is applied
    fillna_on_string -- Fill given value for empty string
    fillna_on_numbers -- Fill given value for empty numbers (int or float)
    fillna_on_uid -- Fill given value for empty uid, which overrides fill_on_numbers for uid
    is_category_as_uid -- Store uid on {base_category}_uid, instead of store the url on {base_category}
    add_category_title -- Add {category}_title columns into the tabular

    Note: It takes O(N) time.
    """
    if document_list is None or len(document_list) == 0:
      return self._createEmptyDataFrame()
    # raise Attribute error if given document does not have portal_type
    portal_type_set = set([x.getPortalType() for x in document_list])
    if len(portal_type_set) != 1:
      raise ValueError('Given documents do not have the same portal type:{}'.format(portal_type_set))
    dict_list = [self._getPropertyDict(x, property_name_list,
                                       is_category_as_uid,
                                       add_category_title) for x in document_list]
    return self.getTabular(dict_list,
                           fillna_on_string=fillna_on_string,
                           fillna_on_number=fillna_on_number,
                           fillna_on_uid=fillna_on_uid)

  security.declareProtected(Permissions.AccessContentsInformation, 'searchResults')
  def searchResults(self, select_dict=None,
                   fillna_on_string=MARKER,
                   fillna_on_number=MARKER,
                   fillna_on_uid=MARKER, **kw):
    """
    Create tabular data based on the portal_catalog.searchResult()

    select_dict -- If select_dict is None, specify all the column ids of catalog table.
    """
    if select_dict is None:
      portal = self.getPortalObject()
      catalog_id = portal.portal_catalog.getDefaultErp5CatalogId()
      default_erp5_catalog = portal.portal_catalog[catalog_id]
      column_id_set = set(default_erp5_catalog.getResultColumnIds())
      sql_search_result_keys_set = set(default_erp5_catalog.getSqlSearchResultKeysList())
      all_column_id_set = column_id_set - sql_search_result_keys_set
      select_dict = dict([(column_id, None) for column_id in all_column_id_set if column_id.startswith('catalog.')])
    search_result = portal.portal_catalog(select_dict=select_dict, **kw)
    return self.getTabular(search_result,
                            fillna_on_string=fillna_on_string,
                            fillna_on_number=fillna_on_number,
                            fillna_on_uid=fillna_on_uid)

  __call__ = getTabular

InitializeClass(TabularDataTool)