"""
  A script for exporting listbox's contents as RSS feed.
  It is called by Listbox_asHTML(in RSS skin) listbox renderer, which queries the listbox
  and passes on column labels and listbox renderer lines. Returns a list
  of items as a piece of xml (because we have to manipulate tag names).

  The implementation is based on RSS 2.0 specification, in a somewhat simplified way
  (e.g. enclosure and source are not implemented, and every guid is a permalink).

  User can limit number of entries by passing "max_articles" in the url (default is 30).

  USAGE:
  The RSS skin is to be used to render a custom rss listbox, which can have columns
  with following titles:
  - title
  - link
  - description
  - author
  - category
  - comments
  - enclosure
  - guid
  - pubDate
  - source
  All elements of an item are optional, however at least one of title or description must be
  present.
  The way an object is presented should be defined in the listbox - the RSS skin passes on
  what is in the listbox, as is. So you can produce your own description, author information
  or publication date. A partial exception to this rule is dates - RSS protocol requires
  it to be compliant to RFC822, so the skin takes care of it - you don't have to (and you
  shouldn't) format date in the listbox. But the way you draw or calculate the
  publication date is entirely up to you.
"""

import six
from Products.PythonScripts.standard import html_quote

items = []
feed_data = {}
request = context.REQUEST

# required channel elements for RSS 2.0 specification
required_field_list = ('title', 'description', 'link')

# required + optional channel elements
allowed_field_list = ('title', 'description', 'link', 'author',
                      'category', 'comments', 'guid', 'pubdate',
                      'thumbnail', )

# figure out which column is which, by using column titles
rss_column_mapping = {}

for index, column_item in enumerate(label_list):
  column_header = column_item[1]
  if column_header.lower() in allowed_field_list:
    rss_column_mapping[column_header.lower()] = index

for line in line_list:
  rss_item_dict = {}
  column_item_list = line.getValueList()
  for header, index in rss_column_mapping.items():
    value_tuple = column_item_list[index]
    # the [0] is a raw value, the [1] is rendered; we want strings rendered (as unicode),
    # but other stuff (like int or DateTime) we want as they are
    if hasattr(value_tuple[0], 'lower'):
      value = html_quote(value_tuple[1])
    else:
      value = value_tuple[0]
    if hasattr(value, 'rfc822'):
      # format dates
      value = value.rfc822()
    rss_item_dict[header] = value
  # build xml from dict (we have to do it here because we need to manipulate tag names
  rss_item_string = ''
  for key, value in six.iteritems(rss_item_dict):
    if key == 'pubdate':
      # pubDate should be returned unconditionally as 'pubDate'
      key = 'pubDate'
    elif key == 'thumbnail' and value:
      # This part prints an image if the "thumbnail" column of listbox is supplied
      rss_item_string += ('\t\t\t<enclosure url="%s" type="image" />\n' % value)
      continue
    rss_item_string += ('\t\t\t<%s>%s</%s>\n' % (key,value or '',key))

  # if required fields not present in listbox columns as label we
  # added theirs appropriate xml dynamically
  for required_field in required_field_list:
    if required_field not in rss_item_dict:
      field_data = ''
      if required_field == 'title':
        if hasattr(line.getBrain(), 'Title'):
          title = line.getBrain().Title()
          if six.PY2:
            title = title.decode('utf-8')
          field_data = html_quote(title or '')
        rss_item_string += ('\t\t\t<%s>%s</%s>\n' % (required_field, field_data, required_field))
      elif required_field == 'link':
        if hasattr(line.getBrain(), 'absolute_url'):
          field_data = line.getBrain().absolute_url() or ''
        rss_item_string += ('\t\t\t<%s>%s</%s>\n' % (required_field, field_data, required_field))
      elif required_field == 'description':
        if hasattr(line.getBrain(), 'getDescription'):
          description = line.getBrain().getDescription()
          if six.PY2:
            description = description.decode('utf-8')
          field_data = html_quote(description or '')
        rss_item_string += ('\t\t\t<%s>%s</%s>\n' % (required_field, field_data,required_field))
  items.append(rss_item_string)

feed_data['listItemInfos'] = tuple(items)

return feed_data
