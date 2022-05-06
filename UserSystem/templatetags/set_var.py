from django import template
register = template.Library()

class SetVarNode(template.Node):
  def __init__(self, var_name, var_value):
    self.var_name = var_name
    self.var_value = var_value
  def render(self, context):
    try:
      value = template.Variable(self.var_value).resolve(context)
    except template.VariableDoesNotExist:
      value = ""
    context[self.var_name] = value
    return u""

  


def set_var(parser, token):
  """
    {% set <var_name> = <var_value> %}
  """
  parts = token.split_contents()
  if len(parts) < 4:
    raise template.TemplateSyntaxError("'set' tag must be of the form: {% set <var_name> = <var_value> %}")
  return SetVarNode(parts[1], parts[3])

# def change_var(parser, token):
#   parts = token.split_contents()
#   if len(parts) < 4:
#     raise template.TemplateSyntaxError("'change' tag must be of the form: {% change <var_name> = <var_value> %}")
#   try:
#     template.Variable(parts[1]) = parts[3]
#   except template.VariableDoesNotExist:
#       raise template.TemplateSyntaxError("'change' tag must be of the form: {% change <var_name> = <var_value> %}")
#   return


register.tag('set', set_var)
# register.tag('change', change_var)