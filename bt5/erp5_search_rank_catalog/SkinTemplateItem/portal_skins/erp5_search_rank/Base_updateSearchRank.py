"""
This method updates the search rank of a document
"""
from zExceptions import Unauthorized

if REQUEST is not None:
  raise Unauthorized

context.Base_zUpdateSearchRank(
  uid=[context.getUid()],
  search_rank=[context.Base_calculateSearchRank()]
)
