from slowapi import Limiter
from slowapi.util import get_remote_address
import os

def get_limit():
    if os.getenv("TESTING") == "true":
        return "1000/minute"
    return "5/minute"

limiter = Limiter(key_func = get_remote_address)