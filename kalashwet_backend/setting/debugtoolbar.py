from django.conf import settings


def show_toolbar(request):
    return settings.DEBUG


DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    "INSERT_BEFORE": "</head>",
    "RENDER_PANELS": True,
}

if settings.DEBUG:
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware", ] + settings.MIDDLEWARE