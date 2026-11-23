"""One log line per request saying which cookies came in and which went out.

Every cookie problem in this project has had the same shape: the server is
certain it set a cookie, the browser is certain it sent one, and the two
are talking about different jars. RequestLogMiddleware records the request
but not its cookies, so that argument could only be settled by reproducing
the journey in a browser with devtools open.

This closes it. The pair of lines that matters looks like:

    [cookies] POST /v1/checkout/cart/ 200 | sent: - | set: xp_visitor(/v1/ Lax),
              xp_cart_token(/v1/ Lax), xp_checkout_binding(/v1/checkout/ Lax HttpOnly)
    [cookies] GET /v1/checkout/session/<id>/ 403 | sent: csrftoken | set: -

Read together they say the cookie was issued and then not returned, which
is the whole diagnosis - no devtools, no reproduction.

NAMES ONLY, NEVER VALUES. xp_checkout_binding, xp_cart_token, csrftoken and
a JWT are all bearer credentials: anyone holding the value can act as that
shopper. A log is copied into tickets and chat messages, so a value written
here is a credential leaked to everyone who reads it. The attributes are
printed instead, because they are what actually decides whether a browser
keeps and returns a cookie, and they give nothing away.
"""
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def _morsel_attrs(morsel):
    """A cookie's attributes, shortest form that still answers the question:
    which jar does this land in, and when will it be sent back."""
    parts = [morsel.get('path') or '/']
    if morsel.get('samesite'):
        parts.append(morsel['samesite'])
    if morsel.get('secure'):
        parts.append('Secure')
    if morsel.get('httponly'):
        parts.append('HttpOnly')
    if morsel.get('partitioned'):
        parts.append('Partitioned')
    if morsel.get('domain'):
        parts.append(f"domain={morsel['domain']}")
    # A delete is a Set-Cookie with a zero lifetime; worth calling out,
    # since "set" and "cleared" otherwise look identical in a log.
    if str(morsel.get('max-age')) == '0':
        parts.append('DELETED')
    return ' '.join(str(p) for p in parts)


class CookieLogMiddleware:
    """Logs the cookie traffic for the routes named in COOKIE_LOG_PREFIXES.

    Scoped by prefix rather than logging everything, because the interesting
    routes are a handful and a line per static file would bury them. Off
    unless COOKIE_LOG_ENABLED, which defaults to DEBUG - this is a debugging
    aid, and on a busy production box it is a line per checkout request.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'COOKIE_LOG_ENABLED', settings.DEBUG)
        self.prefixes = tuple(getattr(settings, 'COOKIE_LOG_PREFIXES', ('/v1/',)))

    def __call__(self, request):
        response = self.get_response(request)
        if not self.enabled or not request.path.startswith(self.prefixes):
            return response
        try:
            self._log(request, response)
        except Exception:  # noqa: BLE001 - a log line must never break a response
            logger.exception('cookie log failed')
        return response

    def _log(self, request, response):
        sent = ', '.join(sorted(request.COOKIES)) or '-'
        issued = ', '.join(
            f'{name}({_morsel_attrs(morsel)})'
            for name, morsel in sorted(getattr(response, 'cookies', {}).items())
        ) or '-'
        origin = request.headers.get('Origin', '') or request.headers.get('Referer', '') or 'same-origin/direct'
        logger.info(
            '[cookies] %s %s %s | from: %s | sent: %s | set: %s',
            request.method, request.get_full_path(), response.status_code,
            origin, sent, issued,
        )
