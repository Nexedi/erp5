if len(old_line_list) == 1 and len(new_line_list) == 1 and \
   new_line_list[0] == old_line_list[0].replace("BTrees._OOBTree","BTrees.OOBTree"):
  return True

return False
