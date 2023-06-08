"""
  Get a chunks of data from a Data Stream, convert it to numpy array
  and return proper start and end for next record.
  
  This script assumes stream has following format.
  {dict1}{dict2}
  {dict3}
  
  And it's possible that last chunk in its last line is incomplete dictionary 
  thus correction needed.
  
"""
import json

chunk_text = ''.join(chunk_list)
#context.log('%s %s %s' %(start, end, len(chunk_text)))

# remove last line as it might be uncomplete and correct start and end offsets
line_list = chunk_text.split('\n')
last_line = line_list[-1]
line_list.pop(-1)

for line in line_list:
  # must have proper format
  assert line.endswith('}')
  assert line.startswith('{')
  
  # fix ' -> "
  line = line.replace("'", '"')
  
  if line.count('{') > 1:
    # multiple concatenated dictionaries in one line, bad format ignore for now
    pass 
  else:
    d = json.loads(line)
    # xxx: save this value as a Data Array identified by data_array_reference

# start and enf offsets may not match existing record structure in stream
# thus corrections in start and end offsets is needed thus we
# return transformed values which is just last line length
start -= len(last_line)
end -= len(last_line)

return start, end
