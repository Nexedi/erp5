from builtins import str
parent = context.getParentValue()
portal_type = context.getPortalType()

step = 10 # XXX configure this ?
index = 0

siblings = [x for x in parent.contentValues(checked_permission='View',
                   filter={"portal_type": portal_type}) if x.getIntIndex()]

if len(siblings):
  index = max([r.getIntIndex() for r in siblings])

index = index + step

if parent.getPortalType() == portal_type:
  reference = "%s.%s" % (parent.getReference(), index)
else:
  reference = str(index)

context.edit(
  int_index=index,
  reference=reference,
)
