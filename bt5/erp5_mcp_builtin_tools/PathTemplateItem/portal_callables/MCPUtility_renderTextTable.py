from Products.ERP5Type.Utils import str2unicode, unicode2str

# Calculate column widths (header + data)
# Note: header titles are already unicode from column_list
MAX_WIDTH = 40
MIN_WIDTH = 3
width_list = []
for column_title in column_list:
  values = [column_title] + [row[column_title] for row in row_list]
  max_len = max(len(v) for v in values)
  max_len = max(max_len, MIN_WIDTH)
  max_len = min(max_len, MAX_WIDTH)
  width_list.append(max_len)

def format_row(r):
  out = []
  for width, column_title, key in zip(width_list, column_list, r):
    try:
      cell = r[key]
    except TypeError:
      cell = key
    diff = len(cell) - width
    if diff > 0:
      cell = cell[:width-3] + u"..."
    elif diff < 0:
      cell = cell + (u" " * abs(diff))
    out.append(cell)
  return u" | ".join(out)

pretext = u"   {}, {} - {} (total count: {})".format(str2unicode(header), start, end, count)
header = format_row(column_list)
line_list = [pretext, u"=" * len(pretext), u"", header, u"=" * len(header)]

for row in row_list:
  line_list.append(format_row(row))

return unicode2str(u'\n'.join(line_list))
