from django import template

register = template.Library()


@register.inclusion_tag('admin/jmbo/inclusion_tags/submit_line.html', takes_context=True)
def submit_row(context):
    """
    Based on django/contrib/admin/templatetags/admin_modify.py version 1.4.1.
    """
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    result = {
        'onclick_attrib': (opts.get_ordered_objects() and change
                            and 'onclick="submitOrderForm();"' or ''),
        'show_delete_link': (not is_popup and context['has_delete_permission']
                              and (change or context['show_delete'])),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': context['has_add_permission'] and
                            not is_popup and (not save_as or context['add']),
        'show_save_and_continue': not is_popup and context['has_change_permission'],
        'is_popup': is_popup,
        'show_save': True,
    }

    if 'original' in context:
        result['show_save_and_publish'] = context['original'].state == 'unpublished'
        result['show_save_and_unpublish'] = context['original'].state == 'published'
    else:
        result['show_save_and_publish'] = True
        result['show_save_and_unpublish'] = False

    return result
