from ZTUtils import make_query
import six
return make_query((item for item in six.iteritems(http_parameter_list) if item[1] is not None))
