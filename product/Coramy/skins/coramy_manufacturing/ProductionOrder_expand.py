## Script (Python) "ProductionOrder_expand"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=
##
# Expands the applied rule associated with the production order

of = context
request = context.REQUEST

applied_rule_list = of.getCausalityRelatedValueList(portal_type="Applied Rule")
if len(applied_rule_list) == 0 :
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Impossible+OF+non+validé.'
                              )
elif len(applied_rule_list) == 1 :

  #  of.expand(applied_rule_id=applied_rule_list[0])
  of.edit()
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Besoins+recalculés.'
                              )
else :
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Problème+de+calcul+des+besoins.'
                              )

request[ 'RESPONSE' ].redirect( redirect_url )
