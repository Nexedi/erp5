from __future__ import absolute_import
from ..SQLQueue import SQLQueue as _SQLQueue
from .SQLBase import SQLBase


class SQLQueue(_SQLQueue, SQLBase):
  pass
