from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from jmbo.models import ModelBase
from jmbo.view_modifiers import DefaultViewModifier


class ObjectDetail(DetailView):

    def get_queryset(self, *args, **kwargs):
        return ModelBase.permitted.get_query_set(
            for_user=getattr(getattr(self, 'request', None), 'user', None)
        )

    def get_template_name(self, *args, **kwargs):
        return 'jmbo/modelbase_detail.html'

    def get_template_name_field(self, *args, **kwargs):
        """This hook allows the model to specify a detail template. When we
        move to class-based generic views this magic will disappear."""
        return 'template_name_field'


class ObjectList(ListView):

    def get_queryset(self, *args, **kwargs):
        return ModelBase.permitted.filter(
            content_type__app_label=kwargs['app_label'],
            content_type__model=kwargs['model']
        ).order_by('-publish_on', '-created')

    def get_template_name(self, *args, **kwargs):
        return 'jmbo/modelbase_list.html'

    def get_paginate_by(self, *args, **kwargs):
        return 10

    def get_view_modifier(self, request, *args, **kwargs):
        return DefaultViewModifier(request, *args, **kwargs)

    def get_extra_context(self, *args, **kwargs):
        # todo: use translated content type model verbose name plural
        return {'title': 'Items', 'model': kwargs['model']}
