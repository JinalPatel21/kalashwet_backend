from rest_framework.response import Response


class StatusMessageUpdateMixin:
    """
    Replaces the default update() response (the serialized object) with
    {"status": true, "message": "<field, field> updated successfully"},
    naming the fields that were actually sent in the request body.
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        print(request.data, "request... data >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        updated_fields = ', '.join(request.data.keys())
        return Response({'status': True, 'message': f'{updated_fields} updated successfully'})
