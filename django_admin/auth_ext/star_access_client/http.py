import json

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from requests import request, HTTPError
from .exception import AccessError


def make_request(uri, method="GET", **kwargs):
    """
    Make request to star access server
    """
    if not getattr(settings, 'STAR_ACCESS_SERVER_URL', None):
        raise ImproperlyConfigured('Requested setting STAR_ACCESS_SERVER_URL, but settings are not configured.')

    url = "{domain}{uri}".format(
        domain=settings.STAR_ACCESS_SERVER_URL,
        uri=uri,
    )

    try:
        response = request(method, url, data=kwargs.get('parm', ''), timeout=20)
        response.raise_for_status()

        result = json.loads(response.content)
        if result.get('code') != 0:
            error = AccessError()
            error.response = response.content
            error.message = result.get('msg')
            raise error
        else:
            return result.get('data')

    except HTTPError as e:
        error = AccessError()
        try:
            error.response = e.response.content
            res = json.loads(e.response.content)
            error.message = res.get('msg')
        except:
            pass
        raise error
    except AccessError as e:
        raise e
    except Exception as e:
        error = AccessError()
        error.message = str(e)
        raise error

