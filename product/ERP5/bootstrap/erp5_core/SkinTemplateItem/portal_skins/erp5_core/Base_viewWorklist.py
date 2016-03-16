module = context.getPortalObject().getDefaultModule(portal_type)

redirect_url = '%s/%s?simulation_state=%s&reset=1' % ( module.absolute_url()
                              , 'view'
                              , simulation_state
                              )


context.REQUEST[ 'RESPONSE' ].redirect( redirect_url )
