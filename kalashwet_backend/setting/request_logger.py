"""Per-module request logging into the database.

Every handled request is stored as an api.RequestLog row. module is the
Django app that served the URL (design, api, user, shopify_sync); anything
else (admin, static, unknown paths) falls back to 'other', so logs can be
fetched module-wise through /v1/logs/?module=<name>.
"""
import logging
import time

from user.choice import PermissionModule


LOG_MODULES = set(PermissionModule.values)
SKIP_PATH_PREFIXES = ('/v1/logs',)
logger = logging.getLogger(__name__)


def _module_for(request):
    resolver = getattr(request, 'resolver_match', None)
    if resolver is not None and resolver.func is not None:
        module = resolver.func.__module__.split('.')[0]
        if module in LOG_MODULES:
            return module
    return 'other'


def _user_label(request):
    user = getattr(request, 'user', None)
    return 'authenticated' if getattr(user, 'is_authenticated', False) else 'anonymous'


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        if request.path.startswith(SKIP_PATH_PREFIXES):
            return response
        try:
            from api.models import RequestLog

            RequestLog.objects.create(
                module=_module_for(request),
                method=request.method,
                # Query strings often contain OTPs, tokens, or personal data.
                path=request.path[:1000],
                status_code=response.status_code,
                duration_ms=int((time.monotonic() - start) * 1000),
                user_label=_user_label(request),
                ip=request.META.get('REMOTE_ADDR', ''),
                error=getattr(request, '_request_log_error', ''),
            )
        except Exception:
            logger.exception('failed to store RequestLog row')
        return response

    def process_exception(self, request, exception):
        # Avoid persisting tracebacks, which can contain credentials and PII.
        request._request_log_error = type(exception).__name__
        return None  # let Django's normal exception handling continue
