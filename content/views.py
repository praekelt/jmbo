from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from category.models import Category
from content.filters import IntervalOrderFilterSet
from content.generic.views import GenericObjectDetail, GenericObjectList
from content.models import ModelBase

class CategoryURL(object):
    def __init__(self, category):
        self.category = category

    def __call__(self, obj):
        return reverse('content_category_object_detail', kwargs={'category_slug': self.category.slug, 'slug': obj.slug})

class CategoryObjectList(GenericObjectList):
    def get_queryset(self):
        return ModelBase.permitted.filter(categories=self.category)
    
    def get_filterset(self, request, queryset):
        return IntervalOrderFilterSet(request.GET, queryset=queryset)
    
    def get_paginate_by(self):
        return 7

    def get_url_callable(self):
        return CategoryURL(category=self.category)
   
    def get_extra_context(self, *args, **kwargs):
        extra_context = super(CategoryObjectList, self).get_extra_context(*args, **kwargs)
        added_context = {'title': self.category.title }
        if extra_context:
            extra_context.update(
                added_context,
            )
        else:
            extra_context = added_context

        return extra_context
    
    def __call__(self, request, category_slug, *args, **kwargs):
        self.category = get_object_or_404(Category, slug__iexact=category_slug)
        return super(CategoryObjectList, self).__call__(request, *args, **kwargs)

category_object_list = CategoryObjectList()

class CategoryObjectDetail(GenericObjectDetail):
    def get_queryset(self):
        return ModelBase.permitted.filter(categories=self.category)
    
    def get_filterset(self, request, queryset):
        return IntervalOrderFilterSet(request.GET, queryset=queryset, action_url=reverse('content_category_object_list', kwargs={'category_slug': self.category.slug}))
    
    def get_extra_context(self, *args, **kwargs):
        extra_context = super(CategoryObjectDetail, self).get_extra_context(*args, **kwargs)
        added_context = {'title': self.category.title }
        if extra_context:
            extra_context.update(
                added_context,
            )
        else:
            extra_context = added_context
        return extra_context
    
    def __call__(self, request, category_slug, *args, **kwargs):
        self.category = get_object_or_404(Category, slug__iexact=category_slug)
        return super(CategoryObjectDetail, self).__call__(request, *args, **kwargs)

category_object_detail = CategoryObjectDetail()
