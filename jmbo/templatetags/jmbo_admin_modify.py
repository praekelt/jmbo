from django import template

register = template.Library()


@register.inclusion_tag('admin/jmbo/submit_line.html', takes_context=True)
def submit_row(context):
    """
    Based on django/contrib/admin/templatetags/admin_modify.py version 1.6.
    Some rules have been changed.
    """
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    ctx = {
        'opts': opts,
        'show_delete_link': (not is_popup and context['has_delete_permission']
                              and change and context.get('show_delete', True)),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': context['has_add_permission'] and
                            not is_popup,
        'show_save_and_continue': not is_popup and context['has_change_permission'],
        'is_popup': is_popup,
        'show_save': True,
        'preserved_filters': context.get('preserved_filters'),
    }
    if context.get('original') is not None:
        ctx['original'] = context['original']

    if 'original' in context:
        ctx['show_save_and_publish'] = context['original'].state == 'unpublished'
        ctx['show_save_and_unpublish'] = context['original'].state == 'published'
    else:
        ctx['show_save_and_publish'] = True
        ctx['show_save_and_unpublish'] = False

    return ctx
