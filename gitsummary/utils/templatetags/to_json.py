from django import template
from django.http import HttpRequest
from tastypie.paginator import Paginator
from django.utils.safestring import mark_safe
from django_git_summary.urls import v1_api


register = template.Library()

@register.filter(name='to_json')
def to_json(value, args={}):
    model = value.model
    resource = v1_api._registry[model._meta.module_name]

    # Dehydrate the bundles in preparation for serialization.
    to_be_serialized = [resource.full_dehydrate(resource.build_bundle(obj=obj)) for obj in value]

    serialized = resource._meta.serializer.serialize(to_be_serialized, 'application/json', None)
    return mark_safe(serialized)
