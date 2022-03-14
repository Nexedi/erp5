from past.builtins import cmp
sync_list = []


# First get sync object and sort them
for synchronization in synchronization_list:
  synchronization_object = context.restrictedTraverse(synchronization)
  sync_list.append(synchronization_object)

def cmp_sync(a,b):
  return cmp(a.getIntIndex(), b.getIntIndex())
sync_list.sort(cmp_sync)

translateString = context.Base_translateString

after_tag = []
for sync in sync_list:
  sub = sync.getDestinationSectionValue()
  pub = sync.getSourceSectionValue()
  if sub.getValidationState() != "validated":
    portal_status_message = translateString("Subscription ${sub} not validated.",
                                            mapping=dict(sub=sub.getTitle()))
    break
  if pub.getValidationState() != "validated":
    portal_status_message = translateString("Publication ${pub} not validated.",
                                            mapping=dict(pub=pub.getTitle()))
    break
  tag = context.getRelativeUrl()
  if reset:
    sub.resetSignatureList()
    sub.resetAnchorList()
    pub.resetSubscriberList()
  context.portal_synchronizations.activate(activity="SQLQueue", tag=tag,
                                           after_method_id=['reset', 'manage_delObjects', 'unindexObject',
                                                            'sendHttpResponse', 'PubSync',
                                                            'activateSyncModif', 'immediateReindexObject'],
                                           after_tag=after_tag).processClientSynchronization(sub.getPath())
  after_tag = [sub.getRelativeUrl(), pub.getRelativeUrl(), tag]
  portal_status_message = translateString("Synchronization started.")

# Add to the integration site view the clock which show activities -Aurel : really necessary ?
context.activate(after_tag=after_tag).getTitle()

if not batch_mode:
  context.Base_redirect(form_id, keep_items = dict(portal_status_message=portal_status_message))
else:
  return sub
