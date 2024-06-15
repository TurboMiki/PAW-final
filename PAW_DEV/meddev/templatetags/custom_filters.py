from django import template

register = template.Library()

@register.filter
def calc_progress(num_used, max_uses):
    if max_uses > 0:
        return (num_used / max_uses) * 100
    else:
        return 0