from django import template
from django.utils.translation import ugettext as _

register = template.Library()

def floathours(hours):
    ret = ""

    if hours <= 0.01:
        return _("nothing")

    # only put hours if we've got more than 60 mins
    if hours > 1.0:
        ret += _("%d hours") % int(hours) + " "
    elif hours == 1.0:
        ret += _("%d hour") % int(hours) + " "

    # only put minutes if it's not zero
    decimins = hours - int(hours)
    mins = int(decimins * 60)

    if mins != 0:
        ret += _("%d mins") % int(mins)

    return ret

register.filter("floathours", floathours)
