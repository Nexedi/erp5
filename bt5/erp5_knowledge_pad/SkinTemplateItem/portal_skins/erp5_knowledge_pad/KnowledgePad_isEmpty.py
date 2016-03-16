"""
Is Knowledge Pad empty (i.e. no gadgets inside).
Use current Pad's layout.
"""
layout = context.KnowledgePad_getBoxColumnLayout()
return not sum([len(x) for x in layout])
