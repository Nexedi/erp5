## Script (Python) "PortalSimulation_updateAssetPrice"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
active_process = context.portal_activities.newActiveProcess(title="Calcul test de valorisation du stock")

result = context.portal_simulation.activate(activity='SQLQueue', priority=3, active_process = active_process ).updateAssetPrice(
		"modele/417P401",
		"""coloris/modele/417P401/1_espace_stuc
taille/enfant/10 ans""",
		"group/Coramy",
		"site/Stock_PF"
	)

#for i in result:
#  print ' '.join(map(lambda x:str(x), i))
print repr(result)


return printed
