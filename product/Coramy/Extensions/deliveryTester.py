def deliveryTester(order=None, root_group=None) :

  from zLOG import LOG
  message = ""
  delivery_list = []

  if root_group is not None and order is not None:

    LOG('ca marche',0,'')
# printing result
    message += "nombre de PathGroup : %s" %len(root_group.group_list)+"\n"
    for group in root_group.group_list :
      message += "\t"+"source : %s _ destination : %s" %(group.source, group.destination)+"\n"
      message += "\t"+"source_section : %s _ destination_section : %s" %(group.source_section, group.destination_section)+"\n"
      message += "\t"+"nombre de DateGroup : %s" %len(group.group_list)+"\n"
      for sub_group in group.group_list :
        message += "\t"*2+"start : %s _ stop : %s" %(sub_group.start_date, sub_group.stop_date)+"\n"
        message += "\t"*2+"nombre de ResourceGroup : %s" %len(sub_group.group_list)+"\n"
        for sub_group2 in sub_group.group_list :
          message += "\t"*3+"resource : %s" %sub_group2.resource+"\n"
          message += "\t"*3+"nombre de VariantGroup : %s" %len(sub_group2.group_list)+"\n"
          for sub_group3 in sub_group2.group_list :
            message += "\t"*4+"categories : %s" %str(sub_group3.category_list)+str(len(sub_group3.category_list))+"\n"

  return message