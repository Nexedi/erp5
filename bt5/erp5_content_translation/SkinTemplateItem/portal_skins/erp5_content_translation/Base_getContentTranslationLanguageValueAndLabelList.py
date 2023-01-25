from Products.ERP5Type.Message import translateString
language_column_list = [(i['id'], str(translateString(i['title'])))
                        for i in context.Localizer.get_languages_map()]
language_column_list.sort()
return language_column_list
