from ssl import create_default_context as ssl_create_default_context, CERT_NONE
from dotenv import load_dotenv as load_dotenvy
from os import getenv as getenvy

load_dotenvy(".envy")


CORE_HOST = getenvy("LYPAY_CORE_HOST")
CORE_PORT = int(getenvy("LYPAY_CORE_PORT"))

SSL = ssl_create_default_context()
SSL.check_hostname = False
SSL.verify_mode = CERT_NONE

EXCLUDED_HEADERS = {
    "transfer-encoding",
    "content-encoding",
    "content-length",
    "connection",
}

VERSION = "v2.6x"
NAME = "Public API"
BUILD = 25
