from ipaddress import ip_address

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from logging import Logger
from http import HTTPStatus

from colorama import Fore, Style, init as c_init

c_init(autoreset=True)


class CustomLog(BaseHTTPMiddleware):
    max_client_length = 15
    max_token_length = 9
    max_message_length = 90

    def __init__(self, app: ASGIApp, app_logger: Logger, blacklist: tuple[str]):
        super().__init__(app)
        self.app_logger = app_logger
        self.blacklist = blacklist


    async def dispatch(self, request, call_next):
        response = await call_next(request)

        if request.url.path not in self.blacklist:
            client_host = self.extract_client_ip(request)
            client = Fore.LIGHTBLACK_EX + Style.BRIGHT + client_host
            client_tab = " " * max(self.max_client_length - len(client_host), 0)

            query = dict(request.query_params)
            token = query.pop("token", "default")
            token_str = Fore.YELLOW + Style.DIM + str(token)
            token_tab = " " * max(self.max_token_length - len(token), 0)

            message = Fore.GREEN + Style.NORMAL + f"{request.method}" + \
            (' ' if request.method == "GET" else '') + \
            Fore.CYAN + Style.NORMAL + f" {request.url.path}"
            message_tab = " " * max(self.max_message_length - len(message) - 5, 0)

            if response.status_code >= 400:
                status_code = Fore.RED
            elif response.status_code >= 300:
                status_code = Fore.YELLOW
            else:
                status_code = Fore.GREEN
            status_code += f"{response.status_code} {HTTPStatus(response.status_code).phrase}"

            self.app_logger.info(
                client + Style.RESET_ALL + client_tab +
                " | " +
                token_str + Style.RESET_ALL + token_tab +
                " | " +
                message + Style.RESET_ALL + message_tab +
                " | " +
                status_code + Style.RESET_ALL
            )

        return response

    def _normalize_ip_candidate(self, value: str | None) -> str | None:
        """очищает, извлекает и проверяет IP-адреса, поддерживая как IPv4, так и IPv6."""
        text = str(value or "").strip().strip('"').strip("'")
        if not text:
            return None

        if text.startswith("[") and "]" in text:
            text = text[1: text.index("]")]
        elif text.count(":") == 1 and "." in text:
            host, port = text.rsplit(":", 1)
            if port.isdigit():
                text = host

        try:
            return str(ip_address(text))
        except ValueError:
            return None

    def _first_forwarded_ip(self, value: str | None) -> str | None:
        """
        Предназначена для извлечения первого валидного IP-адреса из заголовка X-Forwarded-For.
        X-Forwarded-For (XFF) — это стандартный HTTP-заголовок,
        который используется для идентификации реального IP-адреса клиента
        """
        for item in str(value or "").split(","):
            if normalized := self._normalize_ip_candidate(item):
                return normalized
        return None

    def extract_client_ip(self, request) -> str:
        """Извлекает client ip."""
        peer_ip = self._normalize_ip_candidate(request.client.host if request.client else None) or "unknown"
        if peer_ip == "unknown":
            return peer_ip

        if forwarded_ip := self._first_forwarded_ip(request.headers.get("x-forwarded-for")):
            return forwarded_ip
        if real_ip := self._normalize_ip_candidate(request.headers.get("x-real-ip")):
            return real_ip
        return peer_ip
