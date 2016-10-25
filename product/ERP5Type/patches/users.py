from AccessControl.users import BasicUser
if True:
    def getIdOrUserName(self):
        return self.getId() or self.getUserName()

    BasicUser.getIdOrUserName = getIdOrUserName

    def getUserValue(self):
        return None

    BasicUser.getUserValue = getUserValue

    def getLoginValue(self):
        return None

    BasicUser.getLoginValue = getLoginValue

    def getLoginValueList(self, *args, **kw):
        return []

    BasicUser.getLoginValueList = getLoginValueList
