# -*- coding: utf-8 -*-
"""
Sample Wendelin example test code.
"""

from wendelin.bigarray.array_zodb import ZBigArray
import transaction
import numpy as np
from numpy import float64, dtype, cumsum, sin, uint8
import psutil
import os

# generate signal S(t) = M⋅sin(f⋅t)
f = 0.2
M = 15
KB = 1024
MB = 1024*KB
GB = 1024*MB

# Game of Life examples
default_input_ndarray = np.array([[0,0,0,0,0,0],
                                  [0,0,0,1,0,0],
                                  [0,1,0,1,0,0],
                                  [0,0,1,1,0,0],
                                  [0,0,0,0,0,0],
                                  [0,0,0,0,0,0]])

def read(signalv):
  """
  Read zbigarray from ZODB and compute its average/var/sum.
  To run use ERP5Site_readZBigArray external method.
  """
  message_list = []
  message_list.append('sig: %s %s (= %.2fGB)' % \
          ('x'.join('%s' % _ for _ in signalv.shape),
           signalv.dtype, float(signalv.nbytes) / GB))
  a = signalv[:]   # BigArray -> ndarray
  message_list.append('<sig>:\t%s' % a.mean())
  #print('δ(sig):\t%s' % a.var())   # XXX wants to produce temps (var = S (a - <a>)^2
  message_list.append('S(sig):\t%s' % a.sum())
  #cumsum(a) # cummulative sum which will cause memor errors thus disabled!
  message_list.append('S(sig):\t%s' % a.sum())
  return message_list

def generate(signalv):
  """
    Generate a ZBigArray instance bigger than RAM and saves to ZODB.
    To run use external method ERP5Site_generateBigArray
  """
  message_list = []
  message_list.append('gen signal t=0...%.2e  %s  (= %.2fGB) ' %    \
              (len(signalv), signalv.dtype, float(signalv.nbytes) / GB))
  a = signalv[:]  # BigArray -> ndarray
  blocksize = 32*MB//a.itemsize   # will write out signal in such blocks
  for t0 in xrange(0, len(a), blocksize):
    ablk = a[t0:t0+blocksize]

    ablk[:] = 1             # at = 1
    cumsum(ablk, out=ablk)  # at = t-t0+1
    ablk += (t0-1)          # at = t
    ablk *= f               # at = f⋅t
    sin(ablk, out=ablk)     # at = sin(f⋅t)
    ablk *= M               # at = M⋅sin(f⋅t)

    note = 'gen signal blk [%s:%s]  (%.1f%%)' % (t0, t0+len(ablk), 100. * (t0+len(ablk)) / len(a))
    txn = transaction.get()
    txn.note(note)
    txn.commit()
    message_list.append(note)

  return message_list
    
def zbig_array(self, act):
  message_list = []
  ram_nbytes = psutil.virtual_memory().total
  message_list.append('I: RAM: %.2fGB' % (float(ram_nbytes) / GB))

  # let us store in the very root of ZODB
  root = self.getPhysicalRoot()
  
  if act == 'generate':
    sig_dtype = dtype(float64)
    sig_len   = (2*ram_nbytes) // sig_dtype.itemsize
    sig = ZBigArray((sig_len,), sig_dtype)
    root.big_array = sig

    # ZBigArray requirement: before we can compute it (with subobject
    # .zfile) have to be made explicitly known to connection or current
    # transaction committed
    transaction.commit()

    message_list.extend(generate(sig))

  elif act == 'read':
    message_list.extend(read(root.big_array))

  p = psutil.Process(os.getpid())
  m = p.memory_info()
  message_list.append('VIRT: %i MB\tRSS: %iMB' % (m.vms//MB, m.rss//MB))
  return '\n'.join(message_list)

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

  # let us store in the very root of ZODB
  root = self.getPhysicalRoot()

  # create ZBigArray and hook it into DB.
  # please note that it's persistent and never clean up from ZODB so next 
  # execution will raise unless removed from ZODB!
  zlife_area = ZBigArray((6,6), uint8)
  root.life_area_out_of_core = zlife_area

  # ZBigArray requirement: before we can compute it (with subobject
  # .zfile) have to be made explicitly known to connection or current
  # transaction committed
  transaction.commit()

  life_area = root.life_area_out_of_core # our ZBigArray
  life_area  = zlife_area[:,:]  # ZBigArray -> ndarray view of it

  # change the data, exactly as if working with numpy.ndarray but
  # still referencing the ndarray of ZBigArray
  life_area[:,:] = default_input_ndarray

  print_list.append(str(life_area))
  for i in range(4): 
    iterate_2(life_area)
    print_list.append(str(life_area))
  
  return '\n\n'.join(print_list)

def ERP5Site_gameOfLife(self, ndarray_id):
  """
  Run inside an activity and manipulate directly ndarray inside ZODB.
  """
  root = self.getPhysicalRoot()
  zlife_area = getattr(root, ndarray_id) # our ZBigArray
  life_area  = zlife_area[:,:]  # ZBigArray -> ndarray view of it
  # we make a copy, with big volumes maybe not wise
  input_life_area = np.copy(life_area)
  
  # do real calculation on ndarray
  iterate_2(life_area)
  self.log(str(life_area))
  
  if not (input_life_area==life_area).all():
    # input array not equals output array, in this case we can continue
    # until we find a solution or an end stage
    self.portal_activities.activate().ERP5Site_gameOfLife(ndarray_id)

def game_of_life_out_of_core_activities(self):
  """
  Based on Game of Life.
  http://www.labri.fr/perso/nrougier/teaching/numpy/numpy.html
  Using "out-of-core" ndarray stored in Zope's ZODB and activities for load
  balancing.
  """
  # let us store in the very root of ZODB
  root = self.getPhysicalRoot()

  # create ZBigArray and hook it into DB.
  # please note that it's persistent and never clean up from ZODB so next 
  # execution will raise unless removed from ZODB!
  zlife_area = ZBigArray((6,6), uint8)
  root.life_area_out_of_core_persistent = zlife_area

  # ZBigArray requirement: before we can compute it (with subobject
  # .zfile) have to be made explicitly known to connection or current
  # transaction committed
  transaction.commit()

  array_id = 'life_area_out_of_core_persistent'
  life_area = getattr(root, array_id) # our ZBigArray
  life_area  = zlife_area[:,:]  # ZBigArray -> ndarray view of it
  
  # initialise
  life_area[:,:] = default_input_ndarray

  # start calculation in background using activities
  self.portal_activities.activate().ERP5Site_gameOfLife(array_id)

  return 'Started'

def game_of_life(self):
  """
  Based on Game of Life, using vanilla numpy.
  http://www.labri.fr/perso/nrougier/teaching/numpy/numpy.html
  """
  print_list = []
  Z = default_input_ndarray

  print_list.append(str(Z))
  for i in range(4): 
    iterate_2(Z)
    print_list.append(str(Z))
  
  return '\n\n'.join(print_list)