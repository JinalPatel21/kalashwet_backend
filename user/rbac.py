"""Resolution rules for role-based access.

Two levels: a module row (the Django app) and an optional submodule row (one
table inside it). Kept here rather than in the permission class because the
same rules have to produce the same answer in three places - the request
check, the /v1/me/ matrix the panel builds its menu from, and the management
commands - and three copies would drift.

Precedence is most-specific-wins: a table's own row fully replaces the
module's, so a table can hold either more or less than its module. The
alternative (module as a ceiling) cannot express "read-only everywhere except
this one table", which is the usual reason for wanting table rights at all.
"""
from functools import lru_cache

from django.apps import apps

ACTIONS = ('view', 'add', 'change', 'delete')
DENY = {action: False for action in ACTIONS}
ALLOW = {action: True for action in ACTIONS}


@lru_cache(maxsize=None)
def module_tables(module):
    """Lowercase model names defined by `module`, or [] if no such app."""
    try:
        config = apps.get_app_config(module)
    except LookupError:
        return []
    return sorted(model._meta.model_name for model in config.get_models())


def view_submodule(view):
    """Which table `view` acts on, or '' when it doesn't map to exactly one."""
    declared = getattr(view, 'permission_submodule', None)
    if declared is not None:
        return declared
    queryset = getattr(view, 'queryset', None)
    model = getattr(queryset, 'model', None)
    return model._meta.model_name if model is not None else ''


def object_submodule(view, obj):
    """Which table `obj` belongs to, for a detail view whose queryset can hold
    rows governed by different submodules."""
    getter = getattr(view, 'permission_submodule_for_object', None)
    if getter is not None:
        return getter(obj)
    return view_submodule(view)


def effective_permission(role_id, module, submodule=''):
    """The flags that actually apply to (module, submodule) for this role."""
    from .models import RolePermission

    if role_id is None:
        return dict(DENY)

    rows = {
        (row.submodule or ''): row
        for row in RolePermission.objects.filter(role_id=role_id, module=module)
    }
    row = rows.get(submodule) if submodule else None
    if row is None:
        row = rows.get('')
    if row is None:
        return dict(DENY)
    return {action: getattr(row, f'can_{action}') for action in ACTIONS}


def permission_matrix(user):
    """Every module and every table in it, with the rights `user` holds."""
    from .choice import PermissionModule
    from .models import RolePermission

    modules = list(PermissionModule.values)

    if user.is_superuser:
        return {
            module: {
                **ALLOW,
                'tables': {table: dict(ALLOW) for table in module_tables(module)},
            }
            for module in modules
        }

    rows = {}
    if user.role_id is not None:
        for row in RolePermission.objects.filter(role_id=user.role_id):
            rows[(row.module, row.submodule or '')] = {
                action: getattr(row, f'can_{action}') for action in ACTIONS
            }

    matrix = {}
    for module in modules:
        module_flags = rows.get((module, ''), dict(DENY))
        matrix[module] = {
            **module_flags,
            'tables': {
                table: rows.get((module, table), module_flags)
                for table in module_tables(module)
            },
        }
    return matrix
