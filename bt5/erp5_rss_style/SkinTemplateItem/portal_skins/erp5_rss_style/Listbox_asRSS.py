<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string encoding="cdata"><![CDATA[

"""\n
  A script for exporting listbox\'s contents as RSS feed.\n
  It is called by Listbox_asHTML(in RSS skin) listbox renderer, which queries the listbox\n
  and passes on column labels and listbox renderer lines. Returns a list\n
  of items as a piece of xml (because we have to manipulate tag names).\n
\n
  The implementation is based on RSS 2.0 specification, in a somewhat simplified way \n
  (e.g. enclosure and source are not implemented, and every guid is a permalink).\n
\n
  User can limit number of entries by passing "max_articles" in the url (default is 30).\n
\n
  USAGE:\n
  The RSS skin is to be used to render a custom rss listbox, which can have columns\n
  with following titles:\n
  - title\n
  - link\n
  - description\n
  - author\n
  - category\n
  - comments\n
  - enclosure\n
  - guid\n
  - pubDate\n
  - source\n
  All elements of an item are optional, however at least one of title or description must be\n
  present. \n
  The way an object is presented should be defined in the listbox - the RSS skin passes on\n
  what is in the listbox, as is. So you can produce your own description, author information\n
  or publication date. A partial exception to this rule is dates - RSS protocol requires\n
  it to be compliant to RFC822, so the skin takes care of it - you don\'t have to (and you\n
  shouldn\'t) format date in the listbox. But the way you draw or calculate the\n
  publication date is entirely up to you.\n
"""\n
\n
from Products.CMFCore.utils import getToolByName\n
from Products.PythonScripts.standard import html_quote\n
\n
items = []\n
feed_data = {}\n
request = context.REQUEST\n
\n
# required channel elements for RSS 2.0 specification\n
required_field_list = (\'title\', \'description\', \'link\')\n
\n
# required + optional channel elements\n
allowed_field_list = (\'title\', \'description\', \'link\', \'author\', \n
                      \'category\', \'comments\', \'guid\', \'pubdate\',\n
                      \'thumbnail\', )\n
\n
# figure out which column is which, by using column titles\n
rss_column_mapping = {}\n
\n
for index, column_item in enumerate(label_list):\n
  column_header = column_item[1]\n
  if column_header.lower() in allowed_field_list:\n
    rss_column_mapping[column_header.lower()] = index\n
\n
for line in line_list:\n
  rss_item_dict = {}\n
  column_item_list = line.getValueList()\n
  for header, index in rss_column_mapping.items():\n
    value_tuple = column_item_list[index]\n
    # the [0] is a raw value, the [1] is rendered; we want strings rendered (as unicode),\n
    # but other stuff (like int or DateTime) we want as they are\n
    if hasattr(value_tuple[0], \'lower\'):\n
      value = html_quote(value_tuple[1])\n
    else:\n
      value = value_tuple[0]\n
    if hasattr(value, \'rfc822\'):\n
      # format dates\n
      value = value.rfc822()\n
    rss_item_dict[header] = value\n
  # build xml from dict (we have to do it here because we need to manipulate tag names\n
  rss_item_string = \'\'\n
  for key, value in rss_item_dict.items():\n
    if key == \'pubdate\':\n
      # pubDate should be returned unconditionally as \'pubDate\'\n
      key = \'pubDate\'\n
    elif key == \'thumbnail\' and value:\n
      # This part prints an image if the "thumbnail" column of listbox is supplied\n
      rss_item_string += (\'\\t\\t\\t<enclosure url="%s" type="image" />\\n\' % value)\n
      continue\n
    rss_item_string += (\'\\t\\t\\t<%s>%s</%s>\\n\' % (key,value or \'\',key))\n
\n
  # if required fields not present in listbox columns as label we \n
  # added theirs appropriate xml dynamically\n
  for required_field in required_field_list:\n
    if required_field not in rss_item_dict.keys():\n
      field_data = \'\'\n
      if required_field == \'title\':\n
        if hasattr(line.getBrain(), \'Title\'):\n
          field_data = html_quote(unicode(line.getBrain().Title(), \'utf-8\') or \'\')\n
        rss_item_string += (\'\\t\\t\\t<%s>%s</%s>\\n\' % (required_field, field_data, required_field))\n
      elif required_field == \'link\':\n
        if hasattr(line.getBrain(), \'absolute_url\'):\n
          field_data = unicode(line.getBrain().absolute_url(), \'utf-8\' ) or \'\'\n
        rss_item_string += (\'\\t\\t\\t<%s>%s</%s>\\n\' % (required_field, field_data, required_field))\n
      elif required_field == \'description\':\n
        if hasattr(line.getBrain(), \'getDescription\'):\n
          field_data = html_quote(unicode(line.getBrain().getDescription(), \'utf-8\' ) or \'\')\n
        rss_item_string += (\'\\t\\t\\t<%s>%s</%s>\\n\' % (required_field, field_data,required_field))\n
  items.append(rss_item_string)\n
\n
feed_data[\'listItemInfos\'] = tuple(items)\n
\n
return feed_data\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>label_list, line_list</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Listbox_asRSS</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
