# -*- coding: utf-8 -*-

from django import template
import re
from avify.resapp_constants import cathegories, regions
register = template.Library()


@register.simple_tag
def active(request, pattern):
    if re.search(pattern, request.path):
        return 'bg-success'
    return ''

@register.simple_tag
def cath_resolve(cath_id):
    return cathegories[cath_id]

@register.simple_tag
def region_resolve(reg_id):
    return regions[reg_id]
