from dataclasses import dataclass
import threading
from cachecontrol import CacheControl
import requests
from google.auth.transport.requests import Request
from google.oauth2 import id_token

@dataclass(frozen=True)
class Identity:
    sub: str
    email: str

class GoogleRequest:
    def __init__(self):
        self.local = threading.local()

    def __call__(self, *args, **kwargs):
        if not hasattr(self.local, 'request'):
            self.local.request = Request(session=CacheControl(requests.Session()))
        kwargs['timeout'] = 10
        return self.local.request(*args, **kwargs)

class GoogleVerifier:
    def __init__(self, audience):
        if not audience or not audience.endswith('.apps.googleusercontent.com'):
            raise ValueError('Configura GOOGLE_WEB_CLIENT_ID')
        self.audience = audience
        self.request = GoogleRequest()

    def __call__(self, token):
        info = id_token.verify_oauth2_token(token, self.request, audience=self.audience)
        email, sub = info.get('email'), info.get('sub')
        if not isinstance(sub, str) or not sub or not isinstance(email, str):
            raise ValueError('Identidad Google inválida')
        if info.get('email_verified') is not True or not email.lower().endswith('@gmail.com'):
            raise ValueError('Gmail verificado requerido')
        return Identity(sub=sub, email=email.lower())
