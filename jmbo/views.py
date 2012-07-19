from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.db.models import Q

from category.models import Category
from jmbo.generic.views import GenericObjectDetail, GenericObjectList
from jmbo.models import ModelBase
from jmbo.view_modifiers import DefaultViewModifier


class ObjectDetail(GenericObjectDetail):
    def get_queryset(self, *args, **kwargs):
        return ModelBase.permitted

    def get_template_name(self, *args, **kwargs):
        return 'jmbo/modelbase_detail.html'

    def get_template_name_field(self, *args, **kwargs):
        """This hook allows the model to specify a detail template. When we
        move to class-based generic views this magic will disappear."""
        return 'template_name_field'

object_detail = ObjectDetail()


class ObjectList(GenericObjectList):

    def get_queryset(self, *args, **kwargs):
        return ModelBase.permitted.filter(
            content_type__app_label=kwargs['app_label'],
            content_type__model=kwargs['model']
        ).order_by('-id')

    def get_template_name(self, *args, **kwargs):
        return 'jmbo/modelbase_list.html'

    def get_paginate_by(self, *args, **kwargs):
        return 10

    def get_view_modifier(self, request, *args, **kwargs):
        return DefaultViewModifier(request, *args, **kwargs)

    def get_extra_context(self, *args, **kwargs):
        # todo: use translated content type model verbose name plural
        return {'title': 'Items', 'model': kwargs['model']}

object_list = ObjectList()


class ObjectPeek(GenericObjectDetail):
    def get_queryset(self, *args, **kwargs):
        return ModelBase.permitted

    def get_template_name(self, *args, **kwargs):
        return 'jmbo/modelbase_peek.html'

object_peek = ObjectPeek()


class CategoryURL(object):

    def __init__(self, category):
        self.category = category

    def __call__(self, obj=None):
        if self.category and obj:
            return reverse(
                'category_object_detail',
                kwargs={'category_slug': self.category.slug, 'slug': obj.slug}
            )
        elif obj:
            return obj.as_leaf_class().get_absolute_url()
        else:
            return self


class CategoryObjectList(GenericObjectList):

    def get_queryset(self, *args, **kwargs):
        return ModelBase.permitted.filter(
            Q(primary_category=self.category) | Q(categories=self.category)
        ).exclude(pin__category=self.category)

    def get_template_name(self, *args, **kwargs):
        return 'jmbo/modelbase_category_list.html'

    def get_view_modifier(self, request, *args, **kwargs):
        return DefaultViewModifier(
            request,
            base_url=reverse(
                'category_object_list',
                kwargs={'category_slug': self.category.slug}
            ),
            ignore_defaults=True
        )

    def get_paginate_by(self, *args, **kwargs):
        return 10

    def get_url_callable(self, *args, **kwargs):
        return CategoryURL(category=self.category)

    def get_extra_context(self, *args, **kwargs):
        return {
            'title': self.category.title,
            'pinned_object_list': ModelBase.permitted.filter(
                pin__category=self.category
            ).order_by('-created'),
            'category': self.category,
            'url_callable': self.get_url_callable()
        }

    def __call__(self, request, category_slug, *args, **kwargs):
        self.category = get_object_or_404(Category, slug__iexact=category_slug)
        return super(CategoryObjectList, self).__call__(
            request,
            *args,
            **kwargs
        )

category_object_list = CategoryObjectList()


class CategoryObjectDetail(GenericObjectDetail):
    def get_queryset(self, *args, **kwargs):
        return ModelBase.permitted.filter(categories=self.category)

    def get_view_modifier(self, request, *args, **kwargs):
        return DefaultViewModifier(
            request,
            base_url=reverse(
                'category_object_list',
                kwargs={'category_slug': self.category.slug}
            ),
            ignore_defaults=True
        )

    def get_extra_context(self, *args, **kwargs):
        return {
            'title': self.category.title,
            'category': self.category,
            'object': get_object_or_404(
                ModelBase, slug__iexact=kwargs['slug']
            ).as_leaf_class()
        }

    def __call__(self, request, category_slug, *args, **kwargs):
        self.category = get_object_or_404(Category, slug__iexact=category_slug)
        return super(CategoryObjectDetail, self).__call__(
            request,
            *args,
            **kwargs
        )

category_object_detail = CategoryObjectDetail()
