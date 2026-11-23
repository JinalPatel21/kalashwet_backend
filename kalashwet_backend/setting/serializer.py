from django_mongodb_extensions.rest_framework.serializers import (
    MongoModelSerializer as BaseMongoModelSerializer,
)
from rest_framework import serializers


class ObjectIdPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """Renders related ObjectId pks as strings so responses are JSON-serializable."""


    def to_representation(self, value):
        return str(value.pk)


class MongoModelSerializer(BaseMongoModelSerializer):
    """
    Project-wide ModelSerializer base: ObjectId pks (own `id` and ForeignKey
    values) are serialized as strings instead of raw bson ObjectIds, which
    the JSON renderer can't encode.
    """

    serializer_related_field = ObjectIdPrimaryKeyRelatedField
