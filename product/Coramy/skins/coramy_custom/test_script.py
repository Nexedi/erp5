## Script (Python) "test_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
rule = context.getSpecialiseValue()
if rule is not None:
  rule.expand(context, force=1)
