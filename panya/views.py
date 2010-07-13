from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from category.models import Category
from panya.generic.views import GenericObjectDetail, GenericObjectList
from panya.models import ModelBase
from panya.view_modifiers import DefaultViewModifier

class CategoryURL(object):
    def __init__(self, category):
        self.category = category

    def __call__(self, obj=None):
        if obj:
            return reverse('content_category_object_detail', kwargs={'category_slug': self.category.slug, 'slug': obj.slug})
        else:
            return self

class CategoryObjectList(GenericObjectList):
    def get_queryset(self, *args, **kwargs):
        return ModelBase.permitted.filter(categories=self.category)
   
    def get_view_modifier(self, request, *args, **kwargs):
        return DefaultViewModifier(request)

    def get_paginate_by(self, *args, **kwargs):
        return 7

    def get_url_callable(self, *args, **kwargs):
        return CategoryURL(category=self.category)
   
    def get_extra_context(self, *args, **kwargs):
        return {'title': self.category.title }
   
    def __call__(self, request, category_slug, *args, **kwargs):
        self.category = get_object_or_404(Category, slug__iexact=category_slug)
        return super(CategoryObjectList, self).__call__(request, *args, **kwargs)

category_object_list = CategoryObjectList()

class CategoryObjectDetail(GenericObjectDetail):
    def get_queryset(self, *args, **kwargs):
        return ModelBase.permitted.filter(categories=self.category)
    
    def get_view_modifier(self, request, *args, **kwargs):
        return DefaultViewModifier(request, base_url=reverse('content_category_object_list', kwargs={'category_slug': 'news-updates'}), ignore_defaults=True)
    
    def get_extra_context(self, *args, **kwargs):
        return {'title': self.category.title }
    
    def __call__(self, request, category_slug, *args, **kwargs):
        self.category = get_object_or_404(Category, slug__iexact=category_slug)
        return super(CategoryObjectDetail, self).__call__(request, *args, **kwargs)

category_object_detail = CategoryObjectDetail()

class ObjectPeek(GenericObjectDetail):
    def get_queryset(self, *args, **kwargs):
        return ModelBase.permitted

    def get_template_name(self, *args, **kwargs):
        return 'panya/modelbase_peek.html'
    
object_peek = ObjectPeek()
