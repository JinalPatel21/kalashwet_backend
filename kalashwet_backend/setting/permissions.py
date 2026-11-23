from django.conf import settings
from django.utils.crypto import constant_time_compare
from rest_framework.permissions import BasePermission


class IsAuthenticatedOrLogsToken(BasePermission):
    """Normal authenticated access, plus read-only access for monitoring
    tools (Grafana) that send the static X-Logs-Token header. Used on the
    logs API and on the list endpoints the Grafana dashboards read
    (orders, customers, designs, products, variants). Token access can
    never write - only GET/HEAD/OPTIONS pass."""

    def has_permission(self, request, view):
        token = settings.LOGS_API_TOKEN
        supplied = request.headers.get('X-Logs-Token', '')
        if token and supplied and constant_time_compare(supplied, token):
            return request.method in ('GET', 'HEAD', 'OPTIONS')
        return bool(request.user and request.user.is_authenticated)



ACTION_FIELD = {
    'GET': 'view', 'HEAD': 'view', 'OPTIONS': 'view',
    'POST': 'add',
    'PUT': 'change', 'PATCH': 'change',
    'DELETE': 'delete',
}


class HasModulePermission(BasePermission):
    """Role-based module access driven by the RolePermission table
    (managed at runtime via /v1/role-permissions/). The module is the
    Django app the view lives in; a view can override it with a

    `permission_module` attribute. Superusers always pass; users without
    a role, or roles with no row for the module, are denied - fail closed."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_superuser:
            return True
        if user.role_id is None:
            return False
        if getattr(view, 'permission_submodule_for_object', None) is not None:
            return True
        from user.rbac import effective_permission, view_submodule

        module = getattr(view, 'permission_module', type(view).__module__.split('.')[0])
        flags = effective_permission(user.role_id, module, view_submodule(view))
        action = ACTION_FIELD.get(request.method, 'delete')
        return flags[action]

    def has_object_permission(self, request, view, obj):
        if getattr(view, 'permission_submodule_for_object', None) is None:
            return True
        user = request.user
        if user.is_superuser:
            return True
        if user.role_id is None:
            return False
        from user.rbac import effective_permission, object_submodule

        module = getattr(view, 'permission_module', type(view).__module__.split('.')[0])
        flags = effective_permission(user.role_id, module, object_submodule(view, obj))
        action = ACTION_FIELD.get(request.method, 'delete')
        return flags[action]