import logging
import warnings
from typing import Any

import requests
import urllib3

warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class HttpError(RuntimeError):
    """Raised when an HTTP response carries a 4xx or 5xx status code."""

    def __init__(self, status_code: int, body: str) -> None:
        """
        Args:
            status_code: HTTP status code returned by the server.
            body: Response body text (truncated in the exception message).
        """
        self.status_code = status_code
        self.body = body
        super().__init__(f"HTTP {status_code}: {body[:200]}")


class HttpClient:
    """Thin wrapper around :class:`requests.Session` with a fixed base URL.

    All requests disable SSL verification and suppress the associated
    ``urllib3`` warnings.
    """

    def __init__(
        self,
        base_url: str = "",
        default_headers: dict[str, str] | None = None,
        timeout: int = 30,
    ) -> None:
        """
        Args:
            base_url: url prefix for all requests.
            default_headers: Headers merged into every outgoing request.
            timeout: Default socket timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(default_headers or {})
        self.timeout = timeout

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> requests.Response:
        """Send a GET request.

        Args:
            path: URL path appended to ``base_url``.
            params: Query-string parameters.
            headers: Per-request headers that override session defaults.
            timeout: Socket timeout in seconds

        Returns:
            The :class:`requests.Response` object for a successful request.

        Raises:
            HttpError: If the server returns a 4xx or 5xx status code.
        """
        url = self.base_url + path
        logger.debug("GET %s", url)
        try:
            resp = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout or self.timeout,
                verify=False,
            )
            resp.raise_for_status()
            return resp
        except requests.HTTPError as e:
            body = e.response.text if e.response is not None else str(e)
            raise HttpError(
                e.response.status_code if e.response is not None else 0, body
            ) from e

    def post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> requests.Response:
        """Send a POST request with a JSON body.

        Args:
            path: URL path appended to ``base_url``.
            json: Data serialised as JSON and sent as the request body.
            headers: Per-request headers that override session defaults.
            timeout: Socket timeout in seconds.

        Returns:
            The :class:`requests.Response` object for a successful request.

        Raises:
            HttpError: If the server returns a 4xx or 5xx status code.
        """
        url = self.base_url + path
        logger.debug("POST %s", url)
        try:
            resp = self.session.post(
                url,
                json=json,
                headers=headers,
                timeout=timeout or self.timeout,
                verify=False,
            )
            resp.raise_for_status()
            return resp
        except requests.HTTPError as e:
            body = e.response.text if e.response is not None else str(e)
            raise HttpError(
                e.response.status_code if e.response is not None else 0, body
            ) from e
