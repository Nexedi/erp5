from Products.ERP5Type.Cache import CachingMethod
navigation_box_render = context.navigation_box_render
navigation_box_render = CachingMethod(navigation_box_render,
    ("ERP5Site_renderCachedNavigationBox",
     context.portal_membership.getAuthenticatedMember().getIdOrUserName(),
     context.Localizer.get_selected_language(),
     context.portal_url(),
    ),cache_factory='erp5_ui_short')
return navigation_box_render()
