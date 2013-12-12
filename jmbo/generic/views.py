import copy
import traceback

from django.db.models import Q
from django.db.models.fields import related
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import loader
from django.template import RequestContext
from django.utils.translation import ugettext
from django.views.generic import list_detail


class DefaultURL(object):
    def __call__(self, obj=None):
        if obj:
            try:
                return obj.get_absolute_url()
            except AttributeError:
                return ''
        else:
            return self


class GenericBase(object):
    def __init__(self, *args, **kwargs):
        self.params = kwargs
        self.params['view_modifier'] = None
        self.params['url_callable'] = None

    def __call__(self, request, *args, **kwargs):
        self.request = request
        view = copy.copy(self)

        # setup view params
        view.params = view._resolve_view_params(
            request,
            view.defaults,
            *args,
            **kwargs
        )

        # push the view through view modifier
        if 'view_modifier' in view.params['extra_context']:
            view_modifier = view.params['extra_context']['view_modifier']
            if view_modifier:
                if callable(view_modifier):
                    view_modifier = view_modifier(request=request, \
                            *args, **kwargs)
                    view.params['extra_context']['view_modifier'] = \
                            view_modifier
                view = view_modifier.modify(view)

        # Apply possible limit after view modifiers. Django API requires
        # queryset slicing to occur last.
        limit = view.params.pop('limit', 0)
        if limit:
            view.params['queryset'] = view.params['queryset'][:limit]

        return view

    def get_url_callable(self, *args, **kwargs):
        return DefaultURL()

    def _resolve_view_params(self, request, defaults, *args, **kwargs):
        """
        Resolves view params with least ammount of resistance.
        Firstly check for params on urls passed args, then on class
        init args or members, and lastly on class get methods .
        """
        params = copy.copy(defaults)
        params.update(self.params)
        params.update(kwargs)
        resolved_params = {}

        extra_context = {}
        for key in params:
            # grab from provided params.
            value = params[key]

            # otherwise grab from existing params
            if value == None:
                value = self.params[key] if key in self.params else None

            # otherwise grab from class method
            if value == None:
                value = getattr(self, 'get_%s' % key)(request, *args, \
                        **kwargs) if getattr(self, 'get_%s' % key, None) \
                        else None

            if key in defaults:
                resolved_params[key] = value
            else:
                extra_context[key] = value

        if extra_context:
            try:
                resolved_params['extra_context'].update(extra_context)
            except AttributeError:
                resolved_params['extra_context'] = extra_context

        return resolved_params


class GenericObjectList(GenericBase):
    defaults = {
        'queryset': None,
        'paginate_by': None,
        'page': None,
        'allow_empty': True,
        'template_name': None,
        'template_loader': loader,
        'extra_context': None,
        'context_processors': None,
        'template_object_name': 'object',
        'mimetype': None,
        'limit': 0,
    }

    def __call__(self, request, *args, **kwargs):
        # generate our view via genericbase
        view = super(GenericObjectList, self).__call__(
            request,
            *args,
            **kwargs
        )

        # setup object_list params
        queryset = view.params['queryset']
        del view.params['queryset']

        # return object list generic view
        return list_detail.object_list(
            request,
            queryset=queryset,
            **view.params
        )

generic_object_list = GenericObjectList()


class GenericObjectFilterList(GenericObjectList):

    def __call__(self, request, *args, **kwargs):
        # generate our view via genericbase
        view = super(GenericObjectList, self).__call__(
            request,
            *args,
            **kwargs
        )

        # setup object_list params
        queryset = view.params['queryset']
        del view.params['queryset']

        # Filter
        for field in queryset.model._meta.fields:
            if field.name in view.params['extra_context'].keys():
                queryset = queryset.filter(Q(**{"%s__exact" % field.name: \
                        view.params['extra_context'][field.name]}))

        # return object list generic view
        return list_detail.object_list(
            request,
            queryset=queryset,
            **view.params
        )

generic_object_filter_list = GenericObjectFilterList()


class GenericObjectDetail(GenericBase):
    defaults = {
        'queryset': None,
        'object_id': None,
        'slug': None,
        'slug_field': 'slug',
        'template_name_field': None,
        'template_name': None,
        'template_loader': loader,
        'extra_context': None,
        'context_processors': None,
        'template_object_name': 'object',
        'mimetype': None,
    }

    def __call__(self, request, *args, **kwargs):
        # generate our view via genericbase
        view = super(GenericObjectDetail, self).__call__(
            request,
            *args,
            **kwargs
        )

        # setup object_list params
        queryset = view.params['queryset']
        del view.params['queryset']

        # return object list generic view
        return list_detail.object_detail(
            request,
            queryset=queryset,
            **view.params
        )

generic_object_detail = GenericObjectDetail()


class GenericForm(GenericBase):
    defaults = {
        'form_class': None,
        'form_args': {},
        'initial': None,
        'extra_context': None,
        'template_name': None,
        'success_message': None,
    }

    def handle_valid(self, form=None, *args, **kwargs):
        """
        Called after the form has validated.
        """
        # Take a chance and try save a subclass of a ModelForm.
        if hasattr(form, 'save'):
            form.save()
        # Also try and call handle_valid method of the form itself.
        if hasattr(form, 'handle_valid'):
            form.handle_valid(*args, **kwargs)

    def redirect(self, request, *args, **kwargs):
        """
        Redirect after successful form submission.
        Default behaviour is to not redirect and hence
        return the original view.
        """
        return None

    def __call__(self, request, *args, **kwargs):
        # generate our view via genericbase
        view = super(GenericForm, self).__call__(request, *args, **kwargs)

        self.form_class = view.params['form_class']
        self.form_args = view.params['form_args']
        self.initial = view.params['initial']
        self.template_name = view.params['template_name']
        self.success_message = view.params['success_message']

        if request.method == 'POST':
            form = self.form_class(
                data=request.POST,
                files=request.FILES,
                **self.form_args
            )
            if form.is_valid():
                self.handle_valid(form=form, request=request, *args, **kwargs)
                if self.success_message:
                    msg = ugettext(self.success_message)
                    messages.success(request, msg, fail_silently=True)
                redirect = self.redirect(request, *args, **kwargs)
                if redirect:
                    return redirect
        else:
            form = self.form_class(initial=self.initial, **self.form_args)

        context = RequestContext(request, {})
        context.update({
            'form': form,
        })
        context.update(view.params['extra_context'])
        return render_to_response(self.template_name, context)

generic_form_view = GenericForm()
