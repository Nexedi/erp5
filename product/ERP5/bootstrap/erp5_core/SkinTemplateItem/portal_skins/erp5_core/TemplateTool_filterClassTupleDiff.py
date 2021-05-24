if len(old_line_list) == 4 and len(new_line_list) == 1 and \
   old_line_list[0] == '<tuple>' and \
   old_line_list[2] == '<tuple/>' and \
   old_line_list[3] =='</tuple>' and \
   old_line_list[1]== new_line_list[0]:
  return True

return False
