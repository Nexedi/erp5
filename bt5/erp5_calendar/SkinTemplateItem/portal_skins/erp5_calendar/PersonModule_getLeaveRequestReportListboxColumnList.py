from past.builtins import cmp
column_item_list = [ ('person_career_reference', 'Employee Number'),
                     ('person_title', 'Name'), ]

non_translatable_column_item_list = context\
        .PersonModule_getLeaveRequestReportListboxUntranslatableColumnList()
non_translatable_column_item_list.sort(lambda a,b: cmp(a[1], b[1]))

column_item_list.extend(non_translatable_column_item_list)
column_item_list.append(('total', 'Total'))
return column_item_list
