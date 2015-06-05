# -*- coding: utf-8 -*-
"""
 Wendelin extensions code.
"""
from wendelin.bigarray.array_zodb import ZBigArray
import numpy as np

def DataStream_copyCSVToDataArray(self, chunk_list, start, end, \
                                  data_array_reference=None):
  """
    Recieve CSV data and transform it to a numpy array of int.
  """
  chunk_text = ''.join(chunk_list)
  data_array = self.portal_catalog.getResultValue( \
                      portal_type='Data Array', \
                      reference = data_array_reference, \
                      validation_state = 'validated')
  line_list = chunk_text.split('\n')
  size_list = []
  for line in line_list:
    line_item_list = line.split(',')
    size_list.extend([x.strip() for x in line_item_list])

  # save this value as a numpy array (for testing, only create ZBigArray for one variable)
  size_list = [float(x) for x in size_list if x not in ('',)]
  ndarray = np.array(size_list)

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
