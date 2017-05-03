from django import template

register = template.Library()


@register.inclusion_tag('admin/jmbo/modelbase/submit_line.html', takes_context=True)
def submit_row(context):
    """
    Based on django/contrib/admin/templatetags/admin_modify.py version 1.9.
    Add Save and Publish and Save and Unpublish buttons.
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
                            not is_popup and (not save_as or context['add']),
        'show_save_and_continue': not is_popup and context['has_change_permission'],
        'is_popup': is_popup,
        'show_save': True,
        'preserved_filters': context.get('preserved_filters'),
    }
    if context.get('original') is not None:
        ctx['original'] = context['original']
        ctx['show_save_and_publish'] = context['original'].state == 'unpublished'
        ctx['show_save_and_unpublish'] = context['original'].state == 'published'
    else:
        ctx['show_save_and_publish'] = True
        ctx['show_save_and_unpublish'] = False

    return ctx


def xsubmit_row(context):
    """
    Based on django/contrib/admin/templatetags/admin_modify.py version 1.6.
    Some rules have been changed.
    """


    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    show_save = context.get('show_save', True)
    show_save_and_continue = context.get('show_save_and_continue', True)
    ctx = {
        'opts': opts,
        'show_delete_link': (
            not is_popup and context['has_delete_permission'] and
            change and context.get('show_delete', True)
        ),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': (
            context['has_add_permission'] and not is_popup and
            (not save_as or context['add'])
        ),
        'show_save_and_continue': not is_popup and context['has_change_permission'] and show_save_and_continue,
        'is_popup': is_popup,
        'show_save': show_save,
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

