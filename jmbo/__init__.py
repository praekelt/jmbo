from django.conf import settings


USE_GIS = False
if ('atlas' in settings.INSTALLED_APPS) \
    and ('django.contrib.gis' in settings.INSTALLED_APPS) \
    and settings.DATABASES['default']['ENGINE'].startswith('django.contrib.gis.db.backends.'):
    USE_GIS = True


def modify_classes():
    """
    Auto-discover INSTALLED_APPS class_modifiers.py modules and fail silently
    when not present. This forces an import on them to modify any classes they
    may want.
    """
    import copy
    from django.contrib.admin.sites import site
    from importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's class_modifier module.
        try:
            before_import_registry = copy.copy(site._registry)
            import_module('%s.class_modifiers' % app)
        except:
            site._registry = before_import_registry
            # Decide whether to bubble up this error. If the app just
            # doesn't have an class_modifier module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'class_modifiers'):
                raise

modify_classes()

default_app_config = "jmbo.apps.JmboAppConfig"
