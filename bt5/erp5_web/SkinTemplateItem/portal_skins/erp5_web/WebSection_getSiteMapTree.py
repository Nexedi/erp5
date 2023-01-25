"""
  The goal of this script is provide a unified API to generate
  the different lists and trees which are used in a Web Site. This includes
  lists of subsections, lists of pages, site maps, navigation menus.

  If a mapping is provided, the tree structure is mapped
  with object properties defined in the mapping and the result
  can be cached. If no mapping is provided, ZODB documents are provided
  in the tree structure and the result can not be cached.

  The script a representation in the form of a hierarchical site map.
  The structure is provided as a tree so that it is easy to implement
  recursive call with TAL/METAL:

  {
    'url'      : '/erp5/web_site_module/mysite/mysection',
    'level'    : 1,
    'section'  : <some section>,
    'document' : None,
    'subsection' : (
                    {
                      'url'      : '/erp5/web_site_module/mysite/mysection/some-reference',
                      'level'    : 2,
                      'section'  : None,
                      'document' : <some document>,
                      'subsection' : (),
                    },
                    {
                      'url'      : '/erp5/web_site_module/mysite/mysection/subsection',
                      'level'    : 2,
                      'section'  : <some subsection>,
                      'document' : None,
                      'subsection' : (),
                    },
                   ),
  }
"""

def mapObject(property_dict):
  result = {}
  my_object = property_dict.get('section', None)
  if my_object is None: my_object = property_dict.get('document', None)
  if my_object is not None:
    for key in property_mapping:
      result[key] = my_object.getProperty(key)
  result['url'] = property_dict['url']
  result['level'] = property_dict['level']
  result['subsection'] = property_dict['subsection']
  result['section'] = property_dict.get('section', None)
  result['document'] = property_dict.get('document', None)
  return result

def getSiteMapItemTree(section, depth=0, level=None):
  result = []
  if not depth: return result
  if level is None: level = 1
  if include_document or (include_document is None and section.isSiteMapDocumentParent()):
    default_document = None
    if exclude_default_document:
      default_document = section.getDefaultDocumentValue()
    for document in section.getDocumentValueList(sort_on='title'):
      if default_document is not None and default_document.getPhysicalPath() == document.getPhysicalPath():
        continue
      result.append({
                      'url'      : section.getPermanentURL(document),
                      'level'    : level,
                      'section'  : None,
                      'document' : document,
                      'subsection' : None,
                    })
  if include_subsection or (include_subsection is None and section.isSiteMapSectionParent()):
    for subsection in section.contentValues(portal_type=['Web Section', 'Static Web Section'],
                                            sort_on=('int_index', 'translated_title'),
                                            checked_permission='View'):
      if subsection.isVisible():
        subsection_result = getSiteMapItemTree(subsection, depth=depth - 1, level=level + 1)
        if not subsection_result: subsection_result = None
        result.append({
                        'url'      : subsection.absolute_url(),
                        'level'    : level,
                        'section'  : subsection,
                        'document' : None,
                        'subsection'  : subsection_result,
                      })

  if section.isSiteMapSectionParent() and level == 1 and include_site_default_page:
    site = context.getWebSiteValue()
    result.insert(0, {'url': site.absolute_url(), 'level': level, 'section': site, 'document': section.getDefaultDocumentValue(), 'subsection': None})
  if property_mapping:
    return map(mapObject, result)
  return result

return getSiteMapItemTree(context, depth=depth)
