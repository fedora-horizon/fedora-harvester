import logging

import requests

logger = logging.getLogger(__name__)


class HttpError(RuntimeError):
    def __init__(self, status_code: int, body: str):
        self.status_code = status_code
        self.body = body
        super().__init__(f"HTTP {status_code}: {body[:200]}")


class HttpClient:
    def __init__(self, base_url: str = "", default_headers: dict | None = None, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(default_headers or {})
        self.timeout = timeout

    def get(self, path: str, params: dict | None = None,
            headers: dict | None = None, timeout: int | None = None) -> requests.Response:
        url = self.base_url + path
        logger.debug("GET %s", url)
        try:
            resp = self.session.get(url, 
                                    params=params, 
                                    headers=headers,
                                    timeout=timeout or self.timeout,
                                    verify=False)
            resp.raise_for_status()
            return resp
        except requests.HTTPError as e:
            body = e.response.text if e.response is not None else str(e)
            raise HttpError(e.response.status_code if e.response is not None else 0, body) from e

    def post(self, 
             path: str, 
             json: dict | None = None,
             headers: dict | None = None, 
             timeout: int | None = None) -> requests.Response:
        url = self.base_url + path
        logger.debug("POST %s", url)
        try:
            resp = self.session.post(url, 
                                     json=json, 
                                     headers=headers,
                                     timeout=timeout or self.timeout,
                                     verify=False)
            resp.raise_for_status()
            return resp
        except requests.HTTPError as e:
            body = e.response.text if e.response is not None else str(e)
            raise HttpError(e.response.status_code if e.response is not None else 0, body) from e
