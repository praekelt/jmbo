"""
Based on Django's json serializer.

Differences:
1. Serialization can be applied on an iterable or an object.
2. All fields are considered during serialization. The Json serializer
considers only local fields. That makes it cumbersome to use in case of
inherited objects.

Motivation:
The Django serializer framework provides a rich set of operations on data. We
wish to make use of future improvements in the framework.
"""

from StringIO import StringIO

from django.core.serializers.json import Serializer as JsonSerializer
from django.utils.encoding import smart_unicode
from django.conf import settings


class Serializer(JsonSerializer):

    def serialize(self, queryset, **options):
        """
        Serialize a queryset.
        """
        try:
            iter(queryset)
            iterable = True
        except TypeError:
            iterable = False
            queryset = [queryset]

        self.options = options

        self.stream = options.pop("stream", StringIO())
        self.selected_fields = options.pop("fields", None)
        self.use_natural_keys = options.pop("use_natural_keys", False)
        self.selected_properties = options.pop("properties", [])

        self.start_serialization()
        for obj in queryset:
            self.start_object(obj)
            for field in obj._meta.fields:
                if field.serialize:
                    if field.rel is None:
                        if self.selected_fields is None or field.attname in self.selected_fields:
                            self.handle_field(obj, field)
                    else:
                        if self.selected_fields is None or field.attname[:-3] in self.selected_fields:
                            self.handle_fk_field(obj, field)
            for field in obj._meta.many_to_many:
                if field.serialize:
                    if self.selected_fields is None or field.attname in self.selected_fields:
                        self.handle_m2m_field(obj, field)
            if self.selected_properties:
                for prop in self.selected_properties:
                    self.handle_property(obj, prop)
            self.end_object(obj)
        self.end_serialization(single=not iterable)
        return self.getvalue()

    def end_serialization(self, single=False):
        """If single then convert objects list to its first item"""
        if single:
            self.objects = self.objects[0]
        super(Serializer, self).end_serialization()

    def start_object(self, obj):
        self._current = {}
        self._current_properties = {}

    def end_object(self, obj):
        self.objects.append({
            "model"     : smart_unicode(obj._meta),
            "pk"        : smart_unicode(obj._get_pk_val(), strings_only=True),
            "fields"    : self._current,
            "properties": self._current_properties
        })
        self._current = None
        self._current_properties = None

    def handle_field(self, obj, field):
        super(Serializer, self).handle_field(obj, field)
        if field.name == 'image':
            value = self._current[field.name]
            self._current[field.name] = settings.MEDIA_URL + value

    def handle_property(self, obj, prop):
        self._current_properties[prop] = getattr(obj, prop, None)

