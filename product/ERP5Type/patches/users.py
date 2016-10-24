from AccessControl.users import BasicUser
if True:
    def getIdOrUserName(self):
        return self.getId() or self.getUserName()

    BasicUser.getIdOrUserName = getIdOrUserName
