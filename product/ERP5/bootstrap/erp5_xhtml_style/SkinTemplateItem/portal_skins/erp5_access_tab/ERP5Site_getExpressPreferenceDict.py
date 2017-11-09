tool = context.portal_preferences
subscription_status = tool.getPreference('preferred_express_subscription_status')
configuration_status = tool.getPreference('preferred_express_configuration_status')
user_id = tool.getPreference('preferred_express_user_id')

return {'subscription_status':subscription_status,
        'configuration_status':configuration_status,
        'user_id':user_id,
        }
