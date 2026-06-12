"""
Binance Futures Testnet API client.

Handles authentication (HMAC-SHA256 signing), request execution,
and structured logging of all API interactions.
"""

import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode

import httpx

logger = logging.getLogger("trading_bot.client")

# Binance Futures Testnet base URL
TESTNET_BASE_URL = "https://testnet.binancefuture.com"

# Default request timeout in seconds
DEFAULT_TIMEOUT = 10.0


class BinanceAPIError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, status_code: int, code: int, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(
            f"Binance API error {code} (HTTP {status_code}): {message}"
        )


class BinanceTestnetClient:
    """
    Client wrapper for the Binance Futures Testnet REST API.

    Handles request signing, execution, error handling, and logging.
    All requests are sent to the USDT-M Futures testnet.
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = TESTNET_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the Binance testnet client.

        Args:
            api_key: Binance Futures Testnet API key.
            api_secret: Binance Futures Testnet API secret.
            base_url: API base URL (defaults to testnet).
            timeout: HTTP request timeout in seconds.

        Raises:
            ValueError: If api_key or api_secret is empty.
        """
        if not api_key or not api_key.strip():
            raise ValueError(
                "API key is required. Set BINANCE_TESTNET_API_KEY in your .env file."
            )
        if not api_secret or not api_secret.strip():
            raise ValueError(
                "API secret is required. Set BINANCE_TESTNET_API_SECRET in your .env file."
            )

        self._api_key = api_key.strip()
        self._api_secret = api_secret.strip()
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

        self._http = httpx.Client(
            base_url=self._base_url,
            headers={"X-MBX-APIKEY": self._api_key},
            timeout=self._timeout,
        )

        logger.info(
            "Client initialized — base_url=%s, timeout=%.1fs",
            self._base_url,
            self._timeout,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_timestamp(self) -> int:
        """Return current timestamp in milliseconds."""
        return int(time.time() * 1000)

    def _sign_params(self, params: dict) -> dict:
        """
        Add timestamp and HMAC-SHA256 signature to request parameters.

        Args:
            params: Request parameters to sign.

        Returns:
            Parameters dict with 'timestamp' and 'signature' added.
        """
        params = dict(params)  # don't mutate the original
        params["timestamp"] = self._get_timestamp()

        query_string = urlencode(params)
        signature = hmac.new(
            self._api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        params["signature"] = signature
        return params

    def _request(
        self, method: str, endpoint: str, params: dict | None = None, signed: bool = True
    ) -> dict:
        """
        Send an HTTP request to the Binance API.

        Args:
            method: HTTP method ("GET" or "POST").
            endpoint: API endpoint path (e.g., "/fapi/v1/order").
            params: Query/body parameters.
            signed: Whether to sign the request.

        Returns:
            Parsed JSON response as a dict.

        Raises:
            BinanceAPIError: If the API returns an error response.
            httpx.RequestError: On network-level failures.
        """
        params = dict(params or {})

        if signed:
            params = self._sign_params(params)

        logger.debug(
            "API Request  → %s %s | params=%s",
            method.upper(),
            endpoint,
            {k: v for k, v in params.items() if k != "signature"},
        )

        try:
            if method.upper() == "GET":
                response = self._http.get(endpoint, params=params)
            else:
                response = self._http.post(endpoint, params=params)

            logger.debug(
                "API Response ← %s %s | status=%d | body=%s",
                method.upper(),
                endpoint,
                response.status_code,
                response.text[:500],
            )

            # Parse response
            data = response.json()

            # Check for API-level errors
            if response.status_code >= 400 or (
                isinstance(data, dict) and "code" in data and data["code"] < 0
            ):
                error_code = data.get("code", -1)
                error_msg = data.get("msg", "Unknown error")
                logger.error(
                    "API Error — code=%s, msg=%s, endpoint=%s",
                    error_code,
                    error_msg,
                    endpoint,
                )
                raise BinanceAPIError(response.status_code, error_code, error_msg)

            return data

        except httpx.RequestError as exc:
            logger.error(
                "Network error — %s %s: %s", method.upper(), endpoint, exc
            )
            raise

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def get_server_time(self) -> int:
        """
        Get the Binance server time.

        Returns:
            Server time in milliseconds.
        """
        data = self._request("GET", "/fapi/v1/time", signed=False)
        server_time = data["serverTime"]
        local_time = self._get_timestamp()
        drift = abs(server_time - local_time)
        logger.info("Server time: %d (drift: %dms)", server_time, drift)
        return server_time

    def get_exchange_info(self, symbol: str | None = None) -> dict:
        """
        Get exchange information (symbols, filters, precision rules).

        Args:
            symbol: Optional symbol to filter results.

        Returns:
            Exchange info dict.
        """
        data = self._request("GET", "/fapi/v1/exchangeInfo", signed=False)

        if symbol:
            symbols = [
                s for s in data.get("symbols", []) if s["symbol"] == symbol
            ]
            if not symbols:
                raise ValueError(
                    f"Symbol '{symbol}' not found on Binance Futures Testnet."
                )
            return symbols[0]

        return data

    def create_order(self, **params) -> dict:
        """
        Place a new order on Binance Futures Testnet.

        Args:
            **params: Order parameters (symbol, side, type, quantity, etc.)

        Returns:
            Order response dict from the API.

        Raises:
            BinanceAPIError: If the order is rejected.
        """
        return self._request("POST", "/fapi/v1/order", params=params)

    def close(self):
        """Close the underlying HTTP client."""
        self._http.close()
        logger.debug("HTTP client closed.")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
