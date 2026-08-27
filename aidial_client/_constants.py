from urllib.parse import urljoin

import httpx

DEFAULT_MAX_RETRIES = 2
DEFAULT_TIMEOUT = httpx.Timeout(timeout=600.0, connect=5.0)
DEFAULT_CONNECTION_LIMITS = httpx.Limits(
    max_connections=1000, max_keepalive_connections=100
)
INITIAL_RETRY_DELAY = 0.5
MAX_RETRY_DELAY = 8.0
API_PREFIX = "v1/"
METADATA_PREFIX = urljoin(API_PREFIX, "metadata/")
FILES_PREFIX = urljoin(API_PREFIX, "files/")

# DIAL Core exposes folder-shaped resources (agent skills) under /v2.
API_V2_PREFIX = "v2/"
METADATA_V2_PREFIX = urljoin(API_V2_PREFIX, "metadata/")


OPENAI_PREFIX = "openai/"
APPLICATION_PREFIX = urljoin(OPENAI_PREFIX, "applications/")
