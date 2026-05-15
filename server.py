from fastapi import FastAPI

from logging import getLogger, StreamHandler
from sys import stdout

from middleware.logger import CustomLog

from proxy import router as proxy_router


app = FastAPI()

logger = getLogger("app.requests")
logger.setLevel(20)
logger.addHandler(StreamHandler(stdout))

app.add_middleware(CustomLog, app_logger=logger, blacklist=())

app.include_router(proxy_router)
