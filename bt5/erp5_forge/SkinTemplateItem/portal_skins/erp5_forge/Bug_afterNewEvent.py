"""Add a note to increase modification date of bug.

This script has proxy roles, so that even users who cannot modify
the bug can still increase the modification date this way.
"""
from Products.ERP5Type.Message import translateString

context.Base_addEditWorkflowComment(comment=translateString("New comment"))
