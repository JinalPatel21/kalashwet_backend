"""Choice enums for the user app.

PermissionModule is the single list of modules the RBAC system knows about:
RolePermission.module validates against it (so a typo like 'desing' can't
create a dead permission row), and the request logger buckets by it. Adding
a new app = add one member here (+ a small migration for the new choice).
"""
from django.db import models


class PermissionModule(models.TextChoices):
    DESIGN = 'design', 'design'
    API = 'api', 'api'
    USER = 'user', 'user'
    SHOPIFY_SYNC = 'shopify_sync', 'shopify_sync'
    LOYALTY = 'loyalty', 'loyalty'
    AFFILIATE = 'affiliate', 'affiliate'
    PAYMENTS = 'payments', 'payments'
    KIOSK = 'kiosk', 'kiosk'
    STORES = 'stores', 'stores'
    INVENTORY = 'inventory', 'inventory'
    DISCOUNTS = 'discounts', 'discounts'
    TRACKING = 'tracking', 'tracking'
    SETTINGS = 'settings', 'settings'
