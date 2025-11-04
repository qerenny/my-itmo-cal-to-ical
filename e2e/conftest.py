import os
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Generator

import pytest

_SERVER_HOST = "127.0.0.1"
_SERVER_PORT = 5001
_BASE_URL = f"http://{_SERVER_HOST}:{_SERVER_PORT}"
_PING_PATH = "/favicon.ico"
_ENV_VARS = {
    "ITMO_ICAL_ISU_USERNAME": "student",
    "ITMO_ICAL_ISU_PASSWORD": "password",
    "ITMO_ICAL_SENTRY_DSN": "",
    "FLASK_DEBUG": "1",
}


def wait_for_server(url: str, timeout: float = 10.0, interval: float = 0.1) -> None:
    start = time.perf_counter()
    while time.perf_counter() - start < timeout:
        try:
            with urllib.request.urlopen(url) as response:
                if response.status in (200, 404):
                    return
        except urllib.error.HTTPError as exc:
            if exc.code in (200, 404):
                return
        except OSError:
            pass
        time.sleep(interval)
    raise RuntimeError(f"Server at {url} did not become ready within {timeout} seconds")


@pytest.fixture(scope="session", autouse=True)
def app_server() -> Generator[None, None, None]:
    for key, value in _ENV_VARS.items():
        os.environ[key] = value

    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from src.app import app

    thread = threading.Thread(
        target=app.run,
        kwargs={"host": _SERVER_HOST, "port": _SERVER_PORT, "use_reloader": False},
        daemon=True,
    )
    thread.start()
    wait_for_server(_BASE_URL + _PING_PATH)
    yield


@pytest.fixture(scope="session")
def calendar_path() -> str:
    from src.credentials_hashing import get_credentials_hash

    return f"/calendar/{get_credentials_hash('student', 'password')}"


@pytest.fixture(scope="session")
def base_url() -> str:
    return _BASE_URL