from ZTUtils import make_query
return make_query((item for item in http_parameter_list.items() if item[1] is not None))
