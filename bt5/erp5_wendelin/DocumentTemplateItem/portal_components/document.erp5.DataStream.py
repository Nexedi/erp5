# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.
#
##############################################################################
import msgpack
import struct
import numpy as np
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.BigFile import BigFile

class DataStream(BigFile):
  """
  Represents a very big infinite file with a streaming API.
  Usually used to store raw data.
  """

  meta_type = 'ERP5 Data Stream'
  portal_type = 'Data Stream'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.CategoryCore
                    , PropertySheet.SortIndex
                    )

  def iterate(self, start_offset, end_offset):
    """
      Read chunks of data from a Data Stream and yield them.
    """
    data = self._baseGetData()
    for chunk in data.iterate(start_offset, end_offset - start_offset):
      yield chunk

  def readMsgpackChunkList(self, start_offset, end_offset):
    """
      Read chunks of msgpack data from a Data Stream and return (unpacked_data list, offset)
    """
    unpacker = msgpack.Unpacker()
    data = self._baseGetData()
    pos = start_offset
    data_list = []
    for chunk in data.iterate(start_offset, end_offset - start_offset):
      unpacker.feed(chunk)
      while True:
        pos = start_offset + unpacker.tell()
        try:
          #yield unpacker.unpack()
          data_list.append(unpacker.unpack())
        except msgpack.exceptions.OutOfData:
          break
    #raise StopIteration(pos)
    return data_list, pos

  def extractDateTime(self, date_time_holder):
    if isinstance(date_time_holder, int):
      return np.datetime64(date_time_holder, 's')
    # if it is not in, we Expect msgpack.ExtType
    s, ns = struct.unpack(">II", date_time_holder.data)
    return np.datetime64(s, 's') + np.timedelta64(ns, 'ns')

  def readChunkList(self, start_offset, end_offset):
    """
      Read chunks of data from a Data Stream and return them.
    """
    chunk_list = []
    data = self._baseGetData()

    for chunk in data.iterate(start_offset, end_offset - start_offset):
      chunk_list.append(chunk)

    return chunk_list

  def getRecursiveSuccessorValueList(self):
    """
      Return list of all successors (Data Streams) for a Data Stream.
    """
    successor_list = []
    successor = self.getSuccessorValue()
    while successor is not None:
      successor_list.append(successor)
      successor = successor.getSuccessorValue()
    return successor_list

  def getRecursivePredecessorValueList(self):
    """
      Return list of all predecessor (Data Streams) for a Data Stream.
    """
    predecessor_list = []
    predecessor = self.getPredecessorValue()
    while predecessor is not None:
      predecessor_list.append(predecessor)
      predecessor = predecessor.getPredecessorValue()
    return predecessor_list
  
