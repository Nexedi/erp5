"""
Get a list of related documents; wiki relations use API methods, explicit relations
(predecessor etc) get a list of related docs and return the newest (default)
version of each of them.
'all' returns a combined set of all related docs.

"""
# XXX results should be cached as volatile attributes
# XXX-JPS should probably be moved to core API of document
# with dynamic method selection
# getWikiSuccessorValueList = get + upperCase(wiki_successor) + ValueList
# Document_getSimilarityCloud = Document_get + upperCase(cloud) + ValueList
# BG - not much use, they're too different

from Products.ERP5Type.Utils import convertToUpperCase

def getRelatedLatest(category):
  funcname = 'get%sValueList' % convertToUpperCase(category)
  func = getattr(context, funcname)
  return [o.getLatestVersionValue() for o in func()]

relation_id = kw.get('relation_id') # XXX-JPS Change 'what' to more explicit name and include in API of script

if relation_id == 'wiki_predecessor':
  return [i.getObject()
          for i in context.getImplicitPredecessorValueList()]
if relation_id == 'wiki_successor':
  return [i.getObject()
          for i in context.getImplicitSuccessorValueList()]
if relation_id.startswith('related'):
  return getRelatedLatest(relation_id[8:])
if relation_id == 'cloud':
  return context.getSimilarCloudValueList()
if relation_id == 'all':
  dic = {}
  predecessor_value_list = [i.getObject()
                            for i in context.getImplicitPredecessorValueList()]
  successor_value_list = [i.getObject()
                          for i in context.getImplicitSuccessorValueList()]
  similar_value_list = getRelatedLatest('similar')
  for obj in (predecessor_value_list + successor_value_list +
              similar_value_list):
    dic[obj] = None
  return list(dic.keys())

return [] # failover - undefined relation
