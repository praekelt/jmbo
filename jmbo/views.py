from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from jmbo.models import ModelBase, Image


class ObjectDetail(DetailView):
    model = ModelBase

    def get_queryset(self):
        return self.model.permitted.get_queryset(
            for_user=getattr(getattr(self, "request", None), "user", None)
        )

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

    def get_queryset(self):
        return self.model.permitted.filter(
            content_type__app_label=self.kwargs["app_label"],
            content_type__model=self.kwargs["model"]
        )

    def get_context_data(self, **kwargs):
        context = super(ObjectList, self).get_context_data(**kwargs)
        context["paginate_by"] = self.kwargs.get("paginate_by", 10)
        context["title"] = self.kwargs.get("title", "Items")
        return context


def image_scale_url(request, pk, size):
    """Return scaled image URL. This ensures the scale is created by
    Photologue."""

    url = Image.objects.get(pk=pk)._get_SIZE_url(size)
    return HttpResponseRedirect(url)
