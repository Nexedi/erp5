# -*- coding: utf-8 -*-
"""
 Wendelin extensions code.
"""
from wendelin.bigarray.array_zodb import ZBigArray
import numpy as np

def DataStream_copyCSVToDataArray(self, chunk_list, start, end, \
                                  data_array_reference=None):
  """
    Receive CSV data and transform it to a numpy array of floats.
  """
  chunk_text = ''.join(chunk_list)
  
  # compensate possible offset mistmatch
  last_new_line_index = chunk_text.rfind('\n')
  offset_mismatch = len(chunk_text) - last_new_line_index -1
  start = start - offset_mismatch
  end = end - offset_mismatch
  #self.log('%s %s %s' %(len(chunk_list), chunk_text.rfind('\n'), chunk_list))
  
  # remove offset line which is to be processed next call
  chunk_text = chunk_text[:len(chunk_text) - offset_mismatch - 1]
  
  # process left data
  line_list = chunk_text.split('\n')
  size_list = []
  for line in line_list:
    line_item_list = line.split(',')
    size_list.extend([x for x in line_item_list])

  self.log(size_list)

  # save this value as a numpy array (for testing, only create ZBigArray for one variable)
  size_list = [float(x) for x in size_list]
  ndarray = np.array(size_list)

  data_array = self.portal_catalog.getResultValue( \
                      portal_type='Data Array', \
                      reference = data_array_reference, \
                      validation_state = 'validated')
  zarray = data_array.getArray()
  if zarray is None:
    # first time init
    zarray = ZBigArray(ndarray.shape, ndarray.dtype)
    data_array.setArray(zarray)
    zarray = data_array.getArray()

  #self.log('Zarray shape=%s,  To append shape=%s, %s' %(zarray.shape, ndarray.shape, ndarray.itemsize))
    
  # resize so we can add new array data
  old_shape = zarray.shape
  ndarray_shape = ndarray.shape
  new_one = old_shape[0] + ndarray_shape[0]
  zarray.resize((new_one,))
    
  # add new array data to persistent ZBigArray
  zarray[-ndarray_shape[0]:] = ndarray
  
  return start, end
