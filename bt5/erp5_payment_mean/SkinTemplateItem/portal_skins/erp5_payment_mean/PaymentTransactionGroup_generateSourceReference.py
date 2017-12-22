new_id = context.portal_ids.generateNewLengthId(id_group = "PTGR",  default=1)
reference = "PTGR-%06d" % (new_id)
context.setSourceReference(reference)
