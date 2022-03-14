from django import template

register = template.Library()


@register.filter('pagination_range')
def pagination_range(value, current_page):
    """Create a range for a maximum of 10 pages"""
    lower_bound, max_bound = current_page - 3, current_page + 2

    if lower_bound <= 0:
        max_bound += abs(lower_bound)
        lower_bound = 0
    elif max_bound > len(value):
        lower_bound, max_bound = current_page - 5, current_page

    return value[lower_bound:max_bound]
