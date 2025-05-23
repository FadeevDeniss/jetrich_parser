import json

from typing import Any

from requests import Session
from requests.adapters import HTTPAdapter, Retry


class ParsingException(Exception):
    """Base exception that handles errors in parser methods"""


class BaseHttpClient:
    """
    Base HTTP Client that handles http session creation,
    http requests and defines automatic retry.
    """

    def __init__(self, **kwargs):
        auto_retry = Retry(
            total=3,
            backoff_factor=0.2,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods={'POST', 'GET'}
        )

        self.session = Session()
        self.session.mount('https://', HTTPAdapter(max_retries=auto_retry))

    def perform_request(
            self, url: str,
            params: dict[str, Any] = None,
            data: dict[str, Any] = None,
            to_json: bool = True,
            method: str = None,
            auth_header: bool = False,
            **kwargs
    ) -> dict[str, Any] | str:
        """
        Performs an http request and return json-encoded or raw text response.

        """

        if method is None:
            method = 'POST' if any((
                data, kwargs.get('json')
            )) else 'GET'
        headers = kwargs.setdefault('headers', {})

        if auth_header:
            headers.update({'Authorization': f'Bearer {self.auth_token}'})
        response = self.session.request(method, url, params, data, **kwargs)
        if response.status_code != 200:
            raise ParsingException(f'Http request failed with status: {response.status_code}')
        if to_json:
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                raise ParsingException('Response content is not json serializable')

        return response.text
