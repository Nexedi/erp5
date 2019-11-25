from Products.ERP5Type.Log import log
log("ERP5Type_getSecurityCategoryFromArrow is deprecated, "
    "use ERP5Type_getSecurityCategoryFromContent instead")

return context.ERP5Type_getSecurityCategoryFromContent(
    base_category_list, user_name, obj, portal_type)
