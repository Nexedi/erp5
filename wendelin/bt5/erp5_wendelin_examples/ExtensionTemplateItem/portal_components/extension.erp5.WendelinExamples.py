# -*- coding: utf-8 -*-
"""
Sample Wendelin example test code.
"""
import transaction
import numpy as np
from numpy import uint8
import random
import string


def getRandomString():
  return 'test_%s' %''.join([random.choice(string.ascii_letters + string.digits) \
    for _ in range(32)])

# Game of Life examples
default_input_ndarray = np.array([[0,0,0,0,0,0],
                                  [0,0,0,1,0,0],
                                  [0,1,0,1,0,0],
                                  [0,0,1,1,0,0],
                                  [0,0,0,0,0,0],
                                  [0,0,0,0,0,0]])
def iterate_2(Z):
  # Count neighbours
  N = (Z[0:-2,0:-2] + Z[0:-2,1:-1] + Z[0:-2,2:] +
      Z[1:-1,0:-2]                + Z[1:-1,2:] +
      Z[2:  ,0:-2] + Z[2:  ,1:-1] + Z[2:  ,2:])

  # Apply rules
  birth = (N==3) & (Z[1:-1,1:-1]==0)
  survive = ((N==2) | (N==3)) & (Z[1:-1,1:-1]==1)
  Z[...] = 0
  Z[1:-1,1:-1][birth | survive] = 1
  return Z

def game_of_life_out_of_core(self):
  """
  Based on Game of Life.
  http://www.labri.fr/perso/nrougier/teaching/numpy/numpy.html
  Using "out-of-core" ndarray stored in Zope's ZODB.
  """
  print_list = []
  array_reference = 'game_of_life_out_of_core_%s' %getRandomString()
  data_array = self.data_array_module.newContent(
                                        portal_type='Data Array',
                                        reference = array_reference,
                                        version = '001')
  data_array.initArray((6,6), uint8)

  life_area = data_array.getArray()[:,:] # ZBigArray -> ndarray view of it

  # change the data, exactly as if working with numpy.ndarray but
  # still referencing the ndarray of ZBigArray
  life_area[:,:] = default_input_ndarray
  transaction.commit()

  print_list.append(str(life_area))
  for _ in range(4):
    iterate_2(life_area)
    print_list.append(str(life_area))

  return '\n\n'.join(print_list)

def ERP5Site_gameOfLife(self, array_reference):
  """
  Run inside an activity and manipulate directly ndarray inside ZODB.
  """
  data_array = self.portal_catalog.getResultValue(
                                     portal_type = 'Data Array',
                                     reference = array_reference)
  life_area = data_array.getArray()[:,:] # ZBigArray -> ndarray view of it

  # we make a copy, with big volumes maybe not wise
  input_life_area = np.copy(life_area)

  # do real calculation on ndarray
  iterate_2(life_area)
  self.log(str(life_area))

  if not (input_life_area==life_area).all():
    # input array not equals output array, in this case we can continue
    # until we find a solution or an end stage
    self.portal_activities.activate().ERP5Site_gameOfLife(array_reference)

def game_of_life_out_of_core_activities(self):
  """
  Based on Game of Life.
  http://www.labri.fr/perso/nrougier/teaching/numpy/numpy.html
  Using "out-of-core" ndarray stored in Zope's ZODB and activities for load
  balancing.
  """
  array_reference = 'life_area_out_of_core_persistent_%s' %getRandomString()
  data_array = self.data_array_module.newContent(
                                        portal_type='Data Array',
                                        reference = array_reference,
                                        version = '001')
  data_array.initArray((6,6), uint8)

  life_area = data_array.getArray()[:,:] # ZBigArray -> ndarray view of it

  # initialise
  life_area[:,:] = default_input_ndarray

  transaction.commit()

  # start calculation in background using activities
  self.portal_activities.activate().ERP5Site_gameOfLife(array_reference)

  return 'Started'

def game_of_life(self):
  """
  Based on Game of Life, using vanilla numpy.
  http://www.labri.fr/perso/nrougier/teaching/numpy/numpy.html
  """
  print_list = []
  Z = default_input_ndarray

  print_list.append(str(Z))
  for _ in range(4):
    iterate_2(Z)
    print_list.append(str(Z))

  return '\n\n'.join(print_list)

def DataArray_calculateArraySliceAverageAndStore(self, start, end):
  """
    Compute average on a data array slice and store result on an Active Process.
  """
  zarray = self.getArray()
  return np.average(zarray[start:end])