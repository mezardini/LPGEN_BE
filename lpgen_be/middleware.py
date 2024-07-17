# lpgen_be/middleware.py

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.urls import resolve


class SessionAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip custom authentication for the admin panel
        current_url = resolve(request.path_info).url_name
        if current_url and 'admin' in current_url:
            return None

        session_key = request.headers.get('Authorization')
        if session_key:
            try:
                session = Session.objects.get(session_key=session_key)
                user_id = session.get_decoded().get('_auth_user_id')
                request.user = get_user_model().objects.get(pk=user_id)
            except (Session.DoesNotExist, get_user_model().DoesNotExist):
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
        return None
