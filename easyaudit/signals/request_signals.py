from Cookie import SimpleCookie
from django.contrib.sessions.models import Session
from django.core.signals import request_started
from django.utils import timezone

from easyaudit.models import RequestEvent
from easyaudit.settings import WATCH_REQUEST_EVENTS


def should_log_url(url):
    return True


def request_started_handler(sender, environ, **kwargs):
    if not should_log_url(environ['PATH_INFO']):
        return

    if 'HTTP_COOKIE' not in environ:
        return

    cookie = SimpleCookie()
    cookie.load(environ['HTTP_COOKIE'])
    user = None

    if 'sessionid' in cookie:
        session_id = cookie['sessionid'].value

        try:
            session = Session.objects.get(session_key=session_id)
        except Session.DoesNotExist:
            session = None

        if session:
            user_id = session.get_decoded()['_auth_user_id']
            try:
                user = get_user_model().objects.get(id=user_id)
            except:
                user = None

    request_event = RequestEvent.objects.create(
        url=environ['PATH_INFO'],
        method=environ['REQUEST_METHOD'],
        query_string=environ['QUERY_STRING'],
        user=user,
        datetime=timezone.now()
    )


if WATCH_REQUEST_EVENTS:
    request_started.connect(request_started_handler, dispatch_uid='easy_audit_signals_request_started')