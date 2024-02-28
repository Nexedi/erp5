def formatDate(datetime):
  return "%02d%02d%04d" % (datetime.day(), datetime.month(), datetime.year())


# Get the DSN Header and make modifications
is_monthly_dsn = False
header_bloc = [] # list of 2-item tuples
header_line_number = 0
header_length = 0

data = context.getTextContent()
dsn_file_as_list = data.split('\n')

for line_number, line in enumerate(dsn_file_as_list):
  rubric, value = line.split(',', 1)
  value = value.strip('\'')
  if 'S20.G00.05' in rubric:
    header_length += 1
    if rubric == 'S20.G00.05.001':
      is_monthly_dsn = (True if value == '01' else False)
      header_line_number = line_number
    if is_monthly_dsn and rubric == 'S20.G00.05.002':
      value = "03"
    elif is_monthly_dsn and rubric == 'S20.G00.05.004':
      value = "%d" % (int(value) + 1)
    elif is_monthly_dsn and rubric == 'S20.G00.05.007':
      value = "%s" % formatDate(DateTime())

    header_bloc.append((rubric, "'%s'" % value))

# Save the modifications
def formatHeaderElement(element):
  return ','.join(element)

dsn_file_as_list = dsn_file_as_list[:header_line_number] + \
                   map(formatHeaderElement, header_bloc) + \
                   dsn_file_as_list[header_line_number+header_length:]

clone = context.Base_createCloneDocument(batch_mode=1)
clone.setTitle("replacement of %s" % clone.getTitle())
clone.setTextContent('\n'.join(dsn_file_as_list))

# Return clone
msg = "Replacement clone created. Some DSN headers have been modified."
clone.Base_redirect('view', editable_mode=1, keep_items={'portal_status_message': msg})
