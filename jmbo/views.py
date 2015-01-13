from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from jmbo.models import ModelBase
from jmbo.view_modifiers import DefaultViewModifier


class ObjectDetail(DetailView):
    template_name = "jmbo/modelbase_detail.html"

    def get_queryset(self, *args, **kwargs):
        return ModelBase.permitted.get_query_set(
            for_user=getattr(getattr(self, "request", None), "user", None)
        )

    def get_template_name_field(self, *args, **kwargs):
        """This hook allows the model to specify a detail template. When we
        move to class-based generic views this magic will disappear."""
        return 'template_name_field'


class ObjectList(ListView):
    template_name = "jmbo/modelbase_list.html"
    params = {}
    _view_modifier = None

    def get_queryset(self):
        # Must resolve modifier here. get_context_data is called too late.
        self._view_modifier = self.kwargs.get(
            "view_modifier",
            DefaultViewModifier(self.request, *self.args, **self.kwargs)
        )

        qs =  ModelBase.permitted.filter(
            content_type__app_label=self.kwargs["app_label"],
            content_type__model=self.kwargs["model"]
        )

        # Push self through view modifier. Use params dictionary shim so legacy
        # view modifiers do not break.
        view_modifier = self._view_modifier
        if view_modifier:
            if callable(view_modifier):
                view_modifier = view_modifier(request=request,*args, **kwargs)
            self.params["queryset"] = qs
            dc = view_modifier.modify(self)
            return self.params["queryset"]

        return qs

    def get_context_data(self, **kwargs):
        context = super(ObjectList, self).get_context_data(**kwargs)
        context["paginate_by"] = self.kwargs.get("paginate_by", 10)
        context["title"] = self.kwargs.get("title", "Items")
        context["view_modifier"] = self._view_modifier
        return context
