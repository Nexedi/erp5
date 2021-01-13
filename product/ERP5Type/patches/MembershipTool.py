# BBB : allow load of fomer Products.CMFDefault.MembershipTool
# that has been replaced by Products.CMFCore.MembershipTool
import sys, imp
m = 'Products.CMFDefault'
if m not in sys.modules:
  sys.modules[m] = imp.new_module(m)
  m += ".MembershipTool"
  sys.modules[m] = m = imp.new_module(m)
  from Products.CMFCore.MembershipTool import MembershipTool
  m.MembershipTool = MembershipTool
  del m

