from aiohttp import ClientSession, TCPConnector
from fastapi import Request, Response, APIRouter
from dotenv import load_dotenv as load_dotenvy
from os import getenv
from data.config import CORE_HOST, CORE_PORT, SSL, EXCLUDED_HEADERS

router = APIRouter()
load_dotenvy()

ADMIN_TOKEN = getenv("LYPAY_ADMIN_TOKEN")


@router.get("/{path:path}")
async def proxy_path(path: str, request: Request):
    """
    Пересылает GET-запрос на сервер ядра с теми же query-параметрами
    """

    token = getattr(request.state, "token", "<missing>")
    if token == ADMIN_TOKEN:
        return Response(
            content="[403] Forbidden",
            status_code=403
        )

    query_string = str(request.query_params)
    url = f"/{path}" if path else "/"
    if query_string:
        url += f"?{query_string}"

    headers = dict(request.headers)
    headers.pop("host", None)

    try:
        async with ClientSession(connector=TCPConnector(ssl=SSL)) as session:
            response = await session.get(
                f"{CORE_HOST}:{CORE_PORT}" + url,
                headers=headers
            )
            body = await response.read()
    except Exception:
        return Response(
            content="[502] Bad Gateway",
            status_code=502,
        )

    response_headers = {
        key: value for key, value in response.headers.items() if key.lower() not in EXCLUDED_HEADERS
    }

    return Response(
        content=body,
        status_code=response.status,
        headers=response_headers,
    )
