# from ZTUtils import make_query
portal = context.getPortalObject()
Base_translateString = portal.Base_translateString

if not same_type(portal_type, ''):
  # To be improve, but it is enough for Test Result, Suite for now
  raise NotImplementedError('Only support single portal type')

query_params = {}

related_list = portal.portal_catalog(portal_type=portal_type, limit=2, title=context.getTitle())

if len(related_list) == 0:
  redirect_context = context
  message = Base_translateString(
    'No %s Related' % portal_type[0],
    default=Base_translateString('No ${portal_type} related.',
                                 mapping={'portal_type': Base_translateString(portal_type)}))

else:
  redirect_context = related_list[0]
  message = Base_translateString(
    # first, try to get a full translated message with portal types
    "%s related to %s." % (redirect_context.getPortalType(), context.getPortalType()),
     # if not found, fallback to generic translation
    default=Base_translateString('${this_portal_type} related to ${that_portal_type} : ${that_title}.',
      mapping={"this_portal_type": redirect_context.getTranslatedPortalType(),
               "that_portal_type": context.getTranslatedPortalType(),
               "that_title": context.getTitleOrId() }),)

  if (len(related_list) > 1):

    # jump to the module if we can guess it
    module_id = portal.getDefaultModuleId(portal_type, None)
    if module_id is None:
      raise NotImplementedError('Can only search in module, not %s' % portal_type)
    redirect_context = portal.getDefaultModule(portal_type)
    query_params['title'] = context.getTitle()
    query_params['reset'] = True

query_params['portal_status_message'] = message

return redirect_context.Base_redirect(
         'view', keep_items=query_params)
