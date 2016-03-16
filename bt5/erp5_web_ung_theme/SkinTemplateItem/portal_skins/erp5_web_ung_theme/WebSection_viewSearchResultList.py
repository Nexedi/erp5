request = context.REQUEST
field_your_search_text = request.get("field_your_search_text")
portal_type_list = ["Web Page", "Web Illustration", "Web Table"]

keep_items = dict(SearchableText=field_your_search_text,
                  portal_type=portal_type_list)

return context.Base_redirect("", keep_items=keep_items)
