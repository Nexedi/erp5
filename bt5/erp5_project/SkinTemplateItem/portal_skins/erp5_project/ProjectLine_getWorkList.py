# Returns the list of work, ordered by workers.
# A work is a line without childs

def getWorkLineList(line,worker):
  child_list = line.objectValues()
  result = []
  if len(child_list)>0:
    for child in child_list:
      result.extend(getWorkLineList(child,worker))
  else:
    if worker in line.getSourceValueList():
      result.append(line)
  return result

worker_list = context.getParentValue().getSourceValueList()
work_line_list = []
for worker in worker_list:
  work_line_list.extend(getWorkLineList(context,worker))

return work_line_list
