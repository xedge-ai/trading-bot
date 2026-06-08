import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

logger = setup_logger("trading_bot.client")

BASE_URL = "https://testnet.binancefuture.com"


class BinanceClientError(Exception):
    """Raised when Binance API returns an error response."""
    pass


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Append timestamp and HMAC-SHA256 signature to params."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parse response; raise BinanceClientError on API-level errors."""
        try:
            data = response.json()
        except Exception:
            response.raise_for_status()
            raise BinanceClientError("Could not parse API response as JSON.")

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            msg = data.get("msg", "Unknown API error")
            logger.error("Binance API error | code=%s | msg=%s", data["code"], msg)
            raise BinanceClientError(f"API error {data['code']}: {msg}")

        if not response.ok:
            logger.error("HTTP error | status=%s | body=%s", response.status_code, response.text)
            response.raise_for_status()

        return data

    def get(self, endpoint: str, params: Optional[Dict] = None, signed: bool = False) -> Dict:
        params = params or {}
        if signed:
            params = self._sign(params)
        url = BASE_URL + endpoint
        logger.debug("GET %s | params=%s", url, {k: v for k, v in params.items() if k != "signature"})
        try:
            resp = self.session.get(url, params=params, timeout=10)
        except requests.exceptions.RequestException as e:
            logger.error("Network error on GET %s: %s", endpoint, e)
            raise
        logger.debug("GET response | status=%s | body=%s", resp.status_code, resp.text[:500])
        return self._handle_response(resp)

    def post(self, endpoint: str, params: Optional[Dict] = None, signed: bool = True) -> Dict:
        params = params or {}
        if signed:
            params = self._sign(params)
        url = BASE_URL + endpoint
        logger.debug("POST %s | params=%s", url, {k: v for k, v in params.items() if k != "signature"})
        try:
            resp = self.session.post(url, data=params, timeout=10)
        except requests.exceptions.RequestException as e:
            logger.error("Network error on POST %s: %s", endpoint, e)
            raise
        logger.debug("POST response | status=%s | body=%s", resp.status_code, resp.text[:500])
        return self._handle_response(resp)

    def get_account_info(self) -> Dict:
        """Fetch futures account info (sanity check / balance)."""
        return self.get("/fapi/v2/account", signed=True)

    def get_exchange_info(self, symbol: str) -> Dict:
        """Fetch symbol metadata from exchange."""
        return self.get("/fapi/v1/exchangeInfo", params={"symbol": symbol})
