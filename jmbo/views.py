from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from jmbo.models import ModelBase
from jmbo.view_modifiers import DefaultViewModifier


class ObjectDetail(DetailView):
    template_name = "jmbo/modelbase_detail.html"
    view_modifier = None
    # Shim so legacy view modifiers do not break
    params = {"extra_context": {"view_modifier": None}}

    def get_queryset(self):
        qs = ModelBase.permitted.get_query_set(
            for_user=getattr(getattr(self, "request", None), "user", None)
        )

        # Push self through view modifier
        for k, v in self.kwargs.items():
            self.params[k] = v
        if self.view_modifier:
            self.params["extra_context"]["view_modifier"] = self.view_modifier
            if callable(self.view_modifier):
                self.view_modifier = self.view_modifier(request=self.request, **self.kwargs)
            self.params["queryset"] = qs
            dc = self.view_modifier.modify(self)
            return self.params["queryset"]

        return qs

    def get_context_data(self, **kwargs):
        context = super(ObjectDetail, self).get_context_data(**kwargs)
        context["view_modifier"] = self.view_modifier
        return context

    def get_template_name_field(self, *args, **kwargs):
        """This hook allows the model to specify a detail template. When we
        move to class-based generic views this magic will disappear."""
        return 'template_name_field'


class ObjectList(ListView):
    template_name = "jmbo/modelbase_list.html"
    params = {}
    view_modifier = DefaultViewModifier
    # Shim so legacy view modifiers do not break
    params = {"extra_context": {"view_modifier": DefaultViewModifier}}

    def get_queryset(self):
        qs =  ModelBase.permitted.filter(
            content_type__app_label=self.kwargs["app_label"],
            content_type__model=self.kwargs["model"]
        )

        # Push self through view modifier
        for k, v in self.kwargs.items():
            self.params[k] = v
        if self.view_modifier:
            self.params["extra_context"]["view_modifier"] = self.view_modifier
            if callable(self.view_modifier):
                self.view_modifier = self.view_modifier(request=self.request, **self.kwargs)
            self.params["queryset"] = qs
            dc = self.view_modifier.modify(self)
            return self.params["queryset"]

        return qs

    def get_context_data(self, **kwargs):
        context = super(ObjectList, self).get_context_data(**kwargs)
        context["paginate_by"] = self.kwargs.get("paginate_by", 10)
        context["title"] = self.kwargs.get("title", "Items")
        context["view_modifier"] = self.view_modifier
        return context
