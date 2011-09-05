from django.contrib.sites.models import Site


def site(request):
    try:
        site = Site.objects.get_current()
    except Site.DoesNotExist:
        site = None
    return {'site': site}
