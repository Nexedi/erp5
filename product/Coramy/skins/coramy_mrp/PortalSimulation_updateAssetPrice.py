## Script (Python) "PortalSimulation_updateAssetPrice"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
mlist = context.Resource_zGetMovementHistoryList(resource = ["modele/417P401"],
		variation_text = """coloris/modele/417P401/1_espace_stuc
taille/enfant/10 ans""",
		section_category = "group/Coramy",
		node_category= "site/Stock_PF",
                strict_membership = 0,
                simulation_state = ('delivered', 'started', 'stopped', 'invoiced'))

print map(lambda x:x.relative_url, mlist)
print "next" 

result = context.portal_simulation.updateAssetPrice(
		"modele/417P401",
		"""coloris/modele/417P401/1_espace_stuc
taille/enfant/10 ans""",
		"group/Coramy",
		"site/Stock_PF"

	)

for i in result:
  print ' '.join(map(lambda x:str(x), i))

return printed
