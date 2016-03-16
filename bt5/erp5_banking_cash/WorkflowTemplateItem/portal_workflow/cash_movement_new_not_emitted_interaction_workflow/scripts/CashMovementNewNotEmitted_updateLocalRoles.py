obj = state_change['object']
obj.log("will call update security group", "%s, %s" %(obj.getPath(), obj.getDestinationSection()))
obj.assignRoleToSecurityGroup()
