## Script (Python) "sample_order_line_theme_sort"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id
##title=
##
request = context.REQUEST
samples_order = context
sample_order_line_list = samples_order.objectValues()
theme_list = samples_order.getThemes().split("\n")
theme_dict = {}

for index in range(len(theme_list)) :
  theme_dict[theme_list[index]] = index+1

for sample_order_line in sample_order_line_list :
  if sample_order_line.getTheme() in theme_list :
    theme_index = theme_dict[sample_order_line.getTheme()]
  else :
    theme_index = len(theme_list)+1

  sample_order_line.edit(theme_index = theme_index)



redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=lignes+triées.'                       
                              )


request[ 'RESPONSE' ].redirect( redirect_url )
