from django import template


register = template.Library()


@register.simple_tag
def sub(op1, op2):
    return op1 - op2

