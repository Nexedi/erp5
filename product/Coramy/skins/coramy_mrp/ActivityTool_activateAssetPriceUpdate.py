## Script (Python) "ActivityTool_activateAssetPriceUpdate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# Retrieve all resources and commit select
pf_resource_list = context.SimulationTool_zGetResourceList(portal_type=['Modele', 'Assortiment'])
mp_resource_list = context.SimulationTool_zGetResourceList(portal_type=['Tissu', 'Composant'])
context.portal_simulation.commitTransaction()

# Create a new active_process
active_process = context.portal_activities.newActiveProcess(title="Calcul de valorisation du stock")

# Activate updateAssetPrice for PF
commit = 100
for b in list(pf_resource_list)[0:] :
  relative_url =  b.relative_url
  variation_text = b.variation_text
  if relative_url not in (None, ''):
    if variation_text not in (None, '') or b.portal_type != 'Modele':
        print "##Calculate price for %s %s" % (b.relative_url, b.variation_text)
        result = context.portal_simulation.activate(activity='SQLQueue', priority=3, active_process=active_process).updateAssetPrice(
        relative_url, variation_text, "group/Coramy", "site/Stock_PF" )
        #print repr(result)
    else:
        print "###Error variation for %s" % relative_url
    #commit = commit  -1
    #if commit == 0:
    #  # Commit from time to  time
    #  context.portal_simulation.commitTransaction()
    #  commit = 100
  else:
    print "###Error unknow resource '%s'" % b.relative_url

# Activate updateAssetPrice for MP
commit = 100
for b in list(mp_resource_list)[0:] :
  relative_url =  b.relative_url
  variation_text = b.variation_text
  if relative_url not in (None, ''):
    if variation_text not in (None,):
        print "##Calculate price for %s %s" % (b.relative_url, b.variation_text)
        result = context.portal_simulation.activate(activity='SQLQueue', priority=3, active_process=active_process).updateAssetPrice(
        relative_url, variation_text, "group/Coramy", "site/Stock_MP" )
        #print repr(result)
    else:
        print "###Error variation for %s" % relative_url
    #commit = commit  -1
    #if commit == 0:
    #  # Commit from time to  time
    #  context.portal_simulation.commitTransaction()
    #  commit = 100
  else:
    print "###Error unknow resource '%s'" % b.relative_url

return printed
