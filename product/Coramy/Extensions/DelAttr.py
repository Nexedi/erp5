def deleteAttribute(self, id=None):
	if id is not None:
		delattr(self, id)

