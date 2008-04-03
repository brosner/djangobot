
from django import template

register = template.Library()

def do_colorize(value):
    if not value:
        return ""
    result = sum([ord(c) for c in value])
    return "#%X" % result
register.filter("colorize", do_colorize)
