"""Just raise a Validation failed exception.
"""
from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.ERP5Type.Message import Message
raise ValidationFailed(Message('erp5_ui', 'Workflow script raised'))
