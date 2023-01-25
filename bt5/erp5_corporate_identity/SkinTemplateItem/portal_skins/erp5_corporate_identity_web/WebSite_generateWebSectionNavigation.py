'''=============================================================================
                      Create WebSection based Navigation
============================================================================='''

from Products.PythonScripts.standard import html_quote

def buildItem(item, drill_down_depth):
  return menu_item_template % (
    #html_quote(item.getRelativeUrl()),
    html_quote(item.getId()),
    html_quote(item.getTitle()),
    buildWebSectionMenu(getChildWebSectionList(item), drill_down_depth)
  )

def getChildWebSectionList(element):
  breadcrumb_list = element.getBreadcrumbItemList()
  current_section = breadcrumb_list[-1]
  return current_section[1].contentValues(portal_type='Web Section')

def buildWebSectionMenu(element_list, depth):
  if depth < max_depth:
    depth = depth + 1
    display_list = []
    display_items = ''
    display_count = 0

    for section in element_list:
      is_accessible = section.getProperty('authorization_forced') is not True
      is_visible = section.getProperty('visible') is 1
      has_index = section.getProperty('int_index') is not None

      if is_accessible and is_visible and has_index:
        display_list.append(section)

    if len(display_list):
      display_list.sort(key=lambda x: x.getProperty('int_index'), reverse=False)

      for menu_item in display_list:
        if max_items is not None:
          if display_count < max_items:
            display_count = display_count + 1
            display_items = display_items + buildItem(menu_item, depth)
        else:
          display_items = display_items + buildItem(menu_item, depth)
      return menu_list_template % display_items
    else:
      return ''
  else:
    return ''

parent = context
parent_section_list = getChildWebSectionList(parent)
menu_list_template = '''<ul class="ci-web-sitemap-list">%s</ul>'''
menu_item_template = '''<li><a href="./%s"><span class="ci-web-sitemap-item-title">%s</span></a>%s</li>'''
depth = 0
max_depth = max_depth or 2

return buildWebSectionMenu(parent_section_list, depth)
