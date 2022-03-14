from builtins import str
return context.absolute_url() + '/Base_jumpToRelatedObjectList?category.category_uid=' + str(context.getUid())
