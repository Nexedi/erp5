import pandas as pd
import numpy as np
import re
from six.moves import range
import transaction
from DateTime import DateTime
from wendelin.bigarray.array_zodb import ZBigArray
import six


class ZBigArrayConverter(object):
  '''
    ZBigArrayConverter class transforms Portal Catalog or ZSQL Methods results 
    into a Data Array.
    
    It uses the DtypeIdentifyer class map the structure of the input to a proper
    numpy's dtype. 
  '''

  def __init__(self, movements, context):
    self.context = context
    self.movements = movements
  
  def convert(self, reference=None, overwrite=False, add_category=True):
    '''
      convert method will do the transformation of the input into a Data Array
      itself. 
      
      Its parameters are:
        
        - reference: the reference of the Data Array which will be created from the 
          input;
        
        - overwrite: whether the method should overwrite the Data Array if it
          already exists;
          
        - add_category: whether it should add category fields for the movements
          entities or not (should only be true if we are dealing with stock
          movements);
          
      There is a complication related to how Portal Catalog and ZSQL Methods
      order the names of the fields of their results. Both the Results.tuples
      and Results.names methods return the fields in a different order. This
      is not good when working with an array, so we sort alphabetically the 
      fields of each row before import it to the Data Array.
    '''
    my_dtype = DtypeIdentifier(self.movements).identify(add_category=add_category)
    size = len(self.movements)
    reference = reference or 'WendelinJupyter'
    result = self.context.portal_catalog(reference=reference, portal_type='Data Array')
    if len(result) == 0:
      data_array = self.context.data_array_module.newContent(
        portal_type='Data Array', 
        reference=reference
      )
      data_array.initArray((size,), my_dtype)
    elif not overwrite:
      return result[0].getObject()
    else:
      data_array = result[0]
      
    array = data_array.getArray()
    for index in range(len(array)):
      # We need to order everything related to the data schema here. The Results methods
      # `tuples()`, `names` and `data_dictionary` returns the fields in a different order
      # and order is very important in the conversion to a ZBigArray. So we build
      # an array out of the Results instance with the sorted fields.
      ordered_movements = []
      for movement in self.movements:
        new_movement = [movement[key] for key in sorted(self.movements.names())]
        ordered_movements.append(new_movement)
      value = [self.filterItem(item, normalize=False) for item in ordered_movements[index]]
      value.extend([0] * 10)
      array[index:] = tuple(value)
    transaction.commit()
    return data_array.getObject()

  def filterItem(self, item, normalize=False):
    '''
      Method to proccess values and convert them to an improved representation
      that can be used NumPy. Examples are: convertion from DateTime.Datetime
      objects to NumPy.datetime64 and None objects to zeroes.
    '''
    if not item or isinstance(item, type(None)):
      return 0
    if normalize and isinstance(item, (str, unicode)):
      return 0
    elif isinstance(item, DateTime):
      return np.datetime64(item.ISO8601())
    else:
      return item

    
class DtypeIdentifier(object):
  '''
    DtypeIdentifier class is used to identify the best NumPy.dtype that fits
    the input (from the `movements` parameters of the constructor). Then this
    dtype will be used later to create a Data Array.
    
    It can include the movements entities' category fields if the `add_category`
    parameter of the method `identify` is True.
    
  '''
  
  CATEGORY_LIST = 'resource,node,payment,section,mirror_section,function,project,funding,payment_request,movement'.split(',')
  
  def __init__(self, movements):
    self.movements = movements
    self.column_data = self.movements.data_dictionary()
    self.type_dtype_dict = {
      't': 'a',
      'l': 'i8',
      'd': 'datetime64[s]',
      'i': 'i8',
      'n': 'f8',
    }
    
  def identify(self, add_category=True):
    dtypes = self._columns_type_to_dtypes()
    names = sorted(self.movements.names())
    
    if add_category:
      for _ in range(10):
        dtypes.append('a90')
      for attribute in self.CATEGORY_LIST:
        names.append('%s_category' % attribute)    
    
    return np.dtype({
      'names': names, 
      'formats': map(np.dtype, dtypes)
    })

  def _columns_type_to_dtypes(self):
    dtypes = []
    for column in sorted(self.column_data):
      type_ = self.column_data[column]['type']
      size = self.column_data[column]['width']
      dtype = self.type_dtype_dict[type_]
      if dtype == 'a':
        if size > 0:
          dtype += str(size)
        else:
          dtype += '50'
      dtypes.append(dtype)
    return dtypes

def convertResultsToDataArray(self, results, reference='WendelinJupyter'):
  converter = ZBigArrayConverter(results, self)
  array = converter.convert(reference=reference)
  return array

class ZBigArrayExtender(object):
  '''
    ZBigArrayExtender class has the purpose of extending an existing ZBigArray
    using as input another ZBigArray, a Portal Catalog or ZSQL Method results.
  '''
  
  def __init__(self, source, extension):
    self.source = source
    self.extension = extension
    
  def extend(self):
    self.first_part_size = len(self.source)
    self.second_part_size = len(self.extension)
    self.new_total_size = self.first_part_size + self.second_part_size 
    self.source.resize((self.new_total_size,))
    
    if isinstance(self.extension, ZBigArray):
      self._extend_from_zbigarray()
    else:
      self._extend_from_results()
    return self.source
    
  def _extend_from_zbigarray(self):
    if not self.source.dtype == self.extension.dtype:
      raise TypeError('Source and extension data types does not match.')            
    for index, item in enumerate(self.extension):
      self.source[index + self.first_part_size:] = item   
      
  def _extend_from_results(self):
    extension_dtype = DtypeIdentifier(self.extension).identify()
    if not self.source.dtype == extension_dtype:
      raise TypeError('Source and extension data types does not match.')
    for index in range(len(self.extension)):
      # Basically the same problem here with the order of Results instance fields
      # when we convert it to an array.
      ordered_movements = []
      for movement in self.extension:
        new_movement = [movement[key] for key in sorted(self.extension.names())]
        ordered_movements.append(new_movement)
      self.source[index + self.first_part_size:] = tuple(
        [self._filterItem(item, normalize=False) for item in ordered_movements[index]]
      )
  
  def _filterItem(self, item, normalize=False):
    if not item or isinstance(item, type(None)):
      return 0
    if normalize and isinstance(item, (str, unicode)):
      return 0
    elif isinstance(item, DateTime):
      return np.datetime64(item.ISO8601())
    else:
      return item
      
def extendBigArray(self, source, destination):
  return ZBigArrayExtender(
    source, 
    destination
  ).extend()

class CategoryProcessor(object):
  '''
    CategoryProcessor class is responsible for filling all the category fields
    of a Data Array that holds stock movements information. 
    
    For performance reasons, and thanks to NumPy fancy indexing, only one query 
    to the Portal Catalog is made to get all the categories of a given entity 
    (check the FIELDS_WITH_CATEGORY constant). So, in total, 
    `len(FIELDS_WITH_CATEGORY)` queries to Portal Catalog are executed. More
    information about the `fillCategories` method can be found in its own 
    docstring.
    
    It is possible to fill one entity's categories at a time by using the 
    `fields` parameter of the `fillCategories` method. This allows for category
    filling in parallel using activities.
  '''
  
  FIELDS_WITH_CATEGORY = 'resource,node,payment,section,mirror_section,function,project,funding,payment_request,source'.split(',')
  
  def __init__(self, array_reference, context):
    self.context = context.getPortalObject()
    self.array_reference = array_reference
    
  def fillCategoryList(self, fields=None, verbose=False, duplicate_category=False):
    '''
      FillCategoryList is the proper responsible for filling the category fields
      information.
      
      This is the workflow of the method: 
      
        1. Iterate over all the entities that can have categories and for each:
          1.1. Get all the UIDs of this entity in the whole array and for each:
            1.1.1. Get all the categories of this UID using the getCategoryList
              method and store in a dictionary with 2 levels: the name entity 
              where it came from and the UID of this entity
        
        2. Loop over the Data Array and for each of the entities gets the proper
          category UID.  
          
      It would be good to optimize this method at some point. 
    '''
    fields_with_category = fields or self.FIELDS_WITH_CATEGORY

    result = self.context.portal_catalog(portal_type='Data Array', reference=self.array_reference)
    array = result[0].getArray()
    
    fields_objects_categories = {}
    
    categories_df = self._getCategoriesDf()
    for field in fields_with_category:                
      fields_objects_categories[field] = {}
      if field == 'source':
        field_category_name = 'movement_category'
        field_name = 'uid'
      else:
        field_category_name = field+'_category'
        field_name = field+'_uid'
      if verbose:
        print('Processing %s' % field_name)
      uids = [str(row[0]) for row in array[:][[field_name]]]
      objects = self.context.portal_catalog(uid=uids)
      if verbose:
        print('Found %s %s' % (len(objects), field))
        
      for resource in objects:
        categories = resource.getCategoryList()
        category_uids = []
        for category in categories:
          try:
            category_uids.append(str(categories_df.ix[category]['uid']))
          except KeyError:
            if verbose:
              print('Category %s not found from %s' % (category, field_category_name))
              print('...adding to the DataFrame.')
            categories_df.loc[category] = self.context.portal_categories.resolveCategory(category).getUid()
        fields_objects_categories[field][int(resource.getUid())] = ','.join(category_uids)
    
    if duplicate_category:
      total_duplication = 0

    for row in array[0:len(array)]:
      if not row['uid']: continue
      for field in fields_with_category:
        
        if field == 'source':
          field_category_name = 'movement_category'
          field_name = 'uid'
        else:
          field_category_name = field+'_category'
          field_name = field+'_uid'  
        
        resource_uid = int(row[field_name])                
        if resource_uid == 0: continue
        categories = fields_objects_categories[field][resource_uid]
        
        if duplicate_category:     
          for category in categories.split(','):
            new_size = len(array) + 1
            array.resize((new_size,))
            array[new_size-1:] = row.copy()
            array[new_size-1:][field_category_name] = category
            total_duplication += 1
        else:                           
          row[field_category_name] = categories
    transaction.commit()
    if duplicate_category:
      print('Duplication added to the array: %s' % total_duplication)
    return
  
  def _getCategoriesDf(self):
    '''
      _getCategoriesDf creates a Pandas.DataFrame with all categories' UIDs
      and indexes it by each category path. It will be later accessed with the
      result from the getCategoryList method.
    '''
    categories = self.context.portal_catalog(portal_type='Category')
    categories_path = (category.getPath().split('portal_categories/')[1] for category in categories)
    categories_uid = (category.getUid() for category in categories)

    return pd.DataFrame(categories_uid, index=categories_path, columns=['uid'])
    
def fillCategoryList(self, reference, fields=None, verbose=False, duplicate_category=False):
  return CategoryProcessor(reference, self).fillCategoryList(
    verbose=verbose, 
    duplicate_category=duplicate_category
  )

class InventoryDataFrameQuery(object):
  '''
    InventoryDataFrameQuery class is responsbiel for queries in a 
    Pandas.DataFrame created with Data Array filled with stock movements data.
  '''
  
  FIELDS_WITH_CATEGORY = 'resource,node,payment,section,mirror_section,function,project,funding,payment_request'.split(',')

  def __init__(self, df, context, duplicated_categories=False):
    self.df = df
    self.context = context
    self.duplicated_categories = duplicated_categories

  def getMovementHistoryList(self, **kw):
    '''
      Prototype implementation of the Inventory API `getMovementHistoryList`
      using Pandas.DataFrame and Data Array as backend. 
      
      Possible arameters are:
      
        * from_date (>=) - only take rows which date is >= from_date

        * to_date   (<)  - only take rows which date is < to_date
        
        * at_date   (<=) - only take rows which date is <= at_date
        
        * simulation_state - only take rows where simulation state matches 
                           simulation_state
        
        * input_simulation_state - only take rows with specified simulation_state
                         and quantity > 0
        
        * output_simulation_state - only take rows with specified simulation_state
                         and quantity < 0
        
        * only_accountable - Only take into account accountable movements. By
                         default, only movements for which isAccountable() is
                         true will be taken into account.
        
        * omit_input     -  doesn't take into account movement with quantity > 0
        
        * omit_output    -  doesn't take into account movement with quantity < 0
        
        * omit_asset_increase - doesn't take into account movement with asset_price > 0
        
        * omit_asset_decrease - doesn't take into account movement with asset_price < 0
        
        * resource_uid   - only take rows which resource uid matches `resource_uid`
        
        * node_uid       -  only take rows which node uid matches `node_uid`
        
        * payment_uid    -  only take rows which payment uid matches `payment_uid`
        
        * section_uid    -  only take rows which section uid matches `section_uid`
        
        * mirror_section_uid -  only take rows which mirror section uid matches `mirror section_uid`
        
        * resource_<category_name>_uid  - only take rows where the resource categories at
                                        <category_name> includes resource_<category_name>_uid
        
        * node_<category_name>_uid  - only take rows where the node categories at
                                    <category_name> includes node_<category_name>_uid
        
        * payment_<category_name>_uid  - only take rows where the payment categories at
                                       <category_name> includes payment_<category_name>_uid
        
        * section_<category_name>_uid -  only take rows where the section categories at
                                       <category_name> includes section_<category_name>_uid
        
        * mirror_section_<category_name>_uid - only take rows where the mirror section categories at
                                        <category_name> includes mirror_section_<category_name>_uid
        
        * variation_text -  Not implemented yet.
        
        * sub_variation_text - Not implemented yet.
        
        * variation_category - variation or list of possible variations (it is not
                          a cross-search ; SQL query uses OR)
    '''
    kw, self.category_kw = self._filterCategoryParameters(**kw)
    _, self.raw_filter_dict = self.context.portal_simulation._generateKeywordDict(**kw)
    return self._filterDf()
  
  def _filterCategoryParameters(self, **kw):
    category_kw = {}
    keys_to_delete = []
    for key, value in six.iteritems(kw):
      for field in self.FIELDS_WITH_CATEGORY:
        regex = re.compile(r'%s_.*_uid$' % field)
        if regex.match(key):
          field_name = key.split('_')[0] + '_category'
          category_kw[field_name] = value
          keys_to_delete.append(key)
    for key in keys_to_delete:
      del kw[key]
    return kw, category_kw
        
  def _filterDf(self, duplicated_categories=False):
    related_key_dict_filter = self._filterRelatedKeyDictPassthrough()
    omit_dict_filter = self._filterOmitDict()
    simulation_dict_filter = self._filterSimulationDict()
    column_value_dict_filter = self._filterColumnValueDict()
    category_filter = self._filterCategories()

    return self.df[
      column_value_dict_filter &
      related_key_dict_filter &
      omit_dict_filter &
      simulation_dict_filter &
      category_filter
    ]

  def _filterRelatedKeyDictPassthrough(self):
    accountable = self.raw_filter_dict['related_key_dict_passthrough']['is_accountable']
    return self.df['is_accountable'] == int(accountable)
  
  def _filterRelatedKeyDict(self):
    pass
    
  def _filterOmitDict(self):
    base_node_filter = self.df['node_uid'] != self.df['mirror_node_uid']
    base_section_filter = self.df['section_uid'] != self.df['mirror_section_uid']
    # check which values pandas will use when one of these fields below are null
#         base_null_node_filter = self.df['mirror_node_uid']
#         base_null_section_filter = self.df['mirror_section_uid']
#         base_payment_filter = self.df['payment_uid']

    base_filter = (base_node_filter) & (base_section_filter)

    if self.raw_filter_dict['omit_dict']['input'] == 1:
      positive_quantity_filter = (self.df['quantity'] >= 0) & (self.df['is_cancellation'] == 0)
      negative_quantity_filter = (self.df['quantity'] < 0) & (self.df['is_cancellation'] == 1)
      omit_input_output_filter = (positive_quantity_filter) | (negative_quantity_filter)
    elif self.raw_filter_dict['omit_dict']['output'] == 1:
      positive_quantity_filter = (self.df['quantity'] >= 0) & (self.df['is_cancellation'] == 1)
      negative_quantity_filter = (self.df['quantity'] < 0) & (self.df['is_cancellation'] == 0)
      omit_input_output_filter = (positive_quantity_filter) | (negative_quantity_filter)
    else:
      omit_input_output_filter = self._true_array()

    if self.raw_filter_dict['omit_dict']['asset_increase'] == 1:
      negative_price_filter = (self.df['total_price'] < 0) & (self.df['is_cancellation'] == 0)
      positive_price_filter = (self.df['total_price'] >= 0) & (self.df['is_cancellation'] == 1)
      omit_increase_decrease_filter = (negative_price_filter) | (positive_price_filter)
    elif self.raw_filter_dict['omit_dict']['asset_decrease'] == 1:
      negative_price_filter = (self.df['total_price'] < 0) & (self.df['is_cancellation'] == 1)
      positive_price_filter = (self.df['total_price'] >= 0) & (self.df['is_cancellation'] == 0)
      omit_increase_decrease_filter = (negative_price_filter) | (positive_price_filter)
    else:
      omit_increase_decrease_filter = self._true_array()

    return (base_filter) & (omit_input_output_filter) & (omit_increase_decrease_filter)

  def _filterSimulationDict(self):
    simulation_states = self.raw_filter_dict['simulation_dict'].get('simulation_state', [])
    input_simulation_states = self.raw_filter_dict['simulation_dict'].get('input_simulation_state', [])
    output_simulation_states = self.raw_filter_dict['simulation_dict'].get('output_simulation_state', [])

    true_array = self._true_array()

    # dataframe filter madness starts
    if len(simulation_states) == 0:
      simulation_state_filter = true_array
    else:
      simulation_state_filter = self.df['simulation_state'].isin(simulation_states)

    if len(input_simulation_states) == 0:
      input_simulation_filter = true_array
    else:
      input_simulation_state_array = (self.df['simulation_state'].isin(input_simulation_states))
      input_simulation_quantity_positive_array = (self.df['quantity'] > 0) & (self.df['is_cancellation'] == 0)
      input_simulation_quantity_negative_array = (self.df['quantity'] < 0) & (self.df['is_cancellation'] == 1)

      input_simulation_filter = (input_simulation_state_array) & (input_simulation_quantity_positive_array | input_simulation_quantity_negative_array)

    if len(output_simulation_states) == 0:
      output_simulation_filter = true_array
    else:
      output_simulation_state_array = (self.df['simulation_state'].isin(output_simulation_states))
      output_simulation_quantity_positive_array = (self.df['quantity'] > 0) & (self.df['is_cancellation'] == 1)
      output_simulation_quantity_negative_array = (self.df['quantity'] < 0) & (self.df['is_cancellation'] == 0)

      output_simulation_filter = (output_simulation_state_array) & (output_simulation_quantity_positive_array | output_simulation_quantity_negative_array)

    return (simulation_state_filter) | (input_simulation_filter) | (output_simulation_filter)

  def _filterColumnValueDict(self):
    array_classes = (list, tuple)
    columns_values = self.raw_filter_dict['column_value_dict']
    final_filter = self._true_array()
    for key in columns_values.keys():
      if key == 'date':
        range_ = columns_values[key]['range']
        if range_ == 'minmax':
          lower_limit = columns_values[key]['query'][0]
          upper_limit = columns_values[key]['query'][1]
          date_filter = (self.df['date'] > lower_limit) & (self.df['date'] < upper_limit)
        elif range_ == 'min':
          lower_limit = columns_values[key]['query'][0]
          date_filter = (self.df['date'] > lower_limit)
        elif range_ == 'max':
          upper_limit = columns_values[key]['query'][1]
          date_filter = (self.df['date'] < upper_limit)
        final_filter = (date_filter) & (final_filter)
      else:
        values_to_find = columns_values[key]
        values_to_find = values_to_find if isinstance(values_to_find, array_classes) else (values_to_find,)
        columns_values_filter = self.df[key].isin(values_to_find)
        final_filter = (columns_values_filter) & (final_filter)
    return final_filter
  
  def _filterCategories(self):
    partial_filter = self._true_array()
    for field, value in six.iteritems(self.category_kw):
      if self.duplicated_categories:
        partial_filter = (partial_filter) & (self.df[field] == value)
      else:
        partial_filter = (partial_filter) & (self.df[field].str.contains(r'\b%s\b' % value))
    return partial_filter

  def _true_array(self):
    true_array = np.ones((len(self.df),), dtype=bool)
    return true_array
    
def getInventoryDataFrame(self, data_array_reference=None, duplicated_categories=False, as_csv=False,**kw):
  if not data_array_reference:
    if duplicated_categories:
      data_array_reference = 'WendelinJupyterDuplicated'
    else:
      data_array_reference = 'WendelinJupyter'
  array = self.getPortalObject().portal_catalog(
      portal_type='Data Array', 
      reference=data_array_reference
    )[0].getObject().getArray()[:]
  df = pd.DataFrame(array)
  query_result = InventoryDataFrameQuery(
    df, 
    self,
    duplicated_categories=duplicated_categories
  ).getMovementHistoryList(**kw)
  return query_result if not as_csv else query_result.to_csv()