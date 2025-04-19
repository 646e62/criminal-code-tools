import re
from django import template

register = template.Library()

@register.filter
def strip_statute_prefix(section_display, statute_prefix):
    """
    Removes the statute prefix (e.g., 'CDSA ', 'YCJA ', 'Cannabis Act ', 'CC ') from the start of the section display string if present.
    Usage: {{ offence|strip_statute_prefix:result.summary.statute_prefix }}
    """
    if section_display.startswith(statute_prefix):
        return section_display[len(statute_prefix):].strip()
    # Also handle if there is a space after the prefix
    if section_display.lower().startswith(statute_prefix.lower().strip() + ' '):
        return section_display[len(statute_prefix):].strip()
    return section_display
