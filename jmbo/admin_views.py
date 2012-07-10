from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

from jmbo.models import ModelBase


@staff_member_required
def publish_ajax(request):
    obj = ModelBase.objects.get(id=request.REQUEST['id'])
    obj.publish()
    return HttpResponse('published')


@staff_member_required
def unpublish_ajax(request):
    obj = ModelBase.objects.get(id=request.REQUEST['id'])
    obj.unpublish()
    return HttpResponse('unpublished')
