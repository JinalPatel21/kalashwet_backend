from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from django_mongodb_backend.fields import EmbeddedModelArrayField, EmbeddedModelField


class QuietDjangoFilterBackend(DjangoFilterBackend):
    """Same query-param filtering, but skips the browsable API's HTML filter
    form. For models with FK filters the form loads EVERY related row to
    build its dropdowns (str() per option, one query each) - on views like
    loyalty accounts that's a full customer scan per page render."""

    def to_html(self, request, queryset, view):
        return ''


NON_FILTERABLE_FIELD_TYPES = (EmbeddedModelArrayField, EmbeddedModelField, models.JSONField)
TEXT_FIELD_TYPES = (models.CharField, models.TextField, models.EmailField)


def _concrete_fields(model, exclude):
    for field in model._meta.get_fields():
        if not getattr(field, 'concrete', False):
            continue
        if field.name in exclude:
            continue
        if isinstance(field, NON_FILTERABLE_FIELD_TYPES):
            continue
        yield field


def filterable_fields(model, exclude=()):
    """All concrete, non-embedded field names on `model` - for DjangoFilterBackend.filterset_fields."""
    exclude = {'id', *exclude}
    return [field.name for field in _concrete_fields(model, exclude)]


def searchable_fields(model, exclude=()):
    """CharField/TextField/EmailField names on `model` - for SearchFilter.search_fields."""
    exclude = {'id', *exclude}
    return [field.name for field in _concrete_fields(model, exclude) if isinstance(field, TEXT_FIELD_TYPES)]