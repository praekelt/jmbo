def as_div(form):
    """This formatter arranges label, widget, help text and error messages by
    using divs.  Apply to custom form classes, or use to monkey patch form
    classes not under our direct control."""
    # Yes, evil but the easiest way to set this property for all forms.
    form.required_css_class = 'required'

    return form._html_output(
        normal_row=u'<div class="field"><div %(html_class_attr)s>%(label)s %(errors)s <div class="helptext">%(help_text)s</div> %(field)s</div></div>',
        error_row=u'%s',
        row_ender='</div>',
        help_text_html=u'%s',
        errors_on_separate_row=False
    )
