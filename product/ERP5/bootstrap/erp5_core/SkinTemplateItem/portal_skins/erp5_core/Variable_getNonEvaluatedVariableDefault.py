default_value = context.getVariableDefaultExpression(evaluate=0)
if default_value is None:
  # variable_default_expression takes precedence over "static" variable_default_value property
  default_value = repr(context.getVariableDefaultValue())

return default_value
