result = []

IS_MESSAGE_HEADER = True
IS_CONTENT_HEADER = False
IS_BODY_HEADER = True

separator = None

line_buffer = ""

for line in data.split('\n'):
  line = line.strip()
  # If Message Header, try to extract separator or do nothing
  if IS_MESSAGE_HEADER and separator is None:
    if line.lower().startswith('content-type'):
      for key, value in [x.split('=', 1) for x in line.split(';') if '=' in x]:
        if 'boundary' in key.lower():
          separator = value.strip('"')
    continue

  # If Message Header, and separator is set, spot the beginning of the message
  if IS_MESSAGE_HEADER and separator is not None:
    if separator in line:
      IS_MESSAGE_HEADER = False
      IS_CONTENT_HEADER = True
    continue

  # If Content Header, and empty line, the message content starts
  if IS_CONTENT_HEADER and not line:
    IS_CONTENT_HEADER = False
    continue

  # If not Header, and separator is set, print the message
  if not IS_MESSAGE_HEADER and not IS_CONTENT_HEADER and separator is not None:
    if separator in line:
      return printed
    # XXX: find why there are some "3D" in the multipart message
    line = line.replace('3D', '')
    if line[-1] == "=":
      line_buffer = line[:-1]
    else:
      if line_buffer:
        print line_buffer + line
        line_buffer = ""
      else:
        print line

raise ValueError("Multi-part message doesn't follow the standard")
