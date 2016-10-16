# -*- coding: utf-8 -*-

from django import template
import re
register = template.Library()


@register.simple_tag
def active(request, pattern):
    if re.search(pattern, request.path):
        return 'bg-success'
    return ''
