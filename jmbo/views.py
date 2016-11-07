from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from jmbo.models import ModelBase, Image
from jmbo.view_modifiers import DefaultViewModifier


class ObjectDetail(DetailView):
    model = ModelBase
    view_modifier = None
    # Shim so legacy view modifiers do not break
    params = {"extra_context": {"view_modifier": None}}

    def get_queryset(self):
        qs = self.model.permitted.get_queryset(
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

    def get_template_names(self):
        template_names = super(ObjectDetail, self).get_template_names()
        ctype = self.object.content_type
        template_names.extend([
            "%s/%s_detail.html" % (ctype.app_label, ctype.model),
            "%s/%s/object_detail.html" % (ctype.app_label, ctype.model),
            "%s/object_detail.html" % (ctype.app_label),
            "jmbo/object_detail.html",
            "jmbo/modelbase_detail.html"
        ])
        return template_names


class ObjectList(ListView):
    model = ModelBase
    template_name = "jmbo/object_list.html"
    params = {}
    view_modifier = DefaultViewModifier
    # Shim so legacy view modifiers do not break
    params = {"extra_context": {"view_modifier": DefaultViewModifier}}

    def get_queryset(self):
        qs = self.model.permitted.filter(
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


def image_scale_url(request, pk, size):
    """Return scaled image URL. This ensures the scale is created by
    Photologue."""

    url = Image.objects.get(pk=pk)._get_SIZE_url(size)
    return HttpResponseRedirect(url)
