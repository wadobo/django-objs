from django import template
from django.utils.safestring import mark_safe


register = template.Library()


def pbar(value, max, scale):
    ratio = float(value) * 100 / float(max)
    size = ratio * (float(scale) / 100)

    ret = '<div class="progress progress-success"><div class="bar" style="width: %(ratio).2f%%;">%(ratio).2f%%</div></div>' % dict(ratio=ratio)
    return mark_safe(ret)

register.simple_tag(pbar)
