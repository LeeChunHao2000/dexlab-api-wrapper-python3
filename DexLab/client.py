import hashlib
import hmac
import json
import requests
import urllib
from urllib.parse import urlencode

from .constants import *
from .helpers import *

# The order API is still in preparation.
class Client(object):
    def __init__(self, key, secret, subaccount=None, timeout=30):
        self._api_key = key
        self._api_secret = secret
        self._api_subacc = subaccount
        self._api_timeout = int(timeout)

    def _build_headers(self, scope, method, endpoint, query=None):

        headers = {
            'Accept': 'application/json',
            'User-Agent': 'FTX-Trader/1.0',
        }

        return headers

    def _build_url(self, scope, method, endpoint, query=None):
        if query is None:
            query = {}

        if scope.lower() == 'private':
            url = f"{PRIVATE_API_URL}/{VERSION}/{endpoint}"
        else:
            url = f"{PUBLIC_API_URL}/{VERSION}/{endpoint}"

        if method == 'GET':
            return f"{url}?{urlencode(query, True, '/[]')}" if len(query) > 0 else url
        else:
            return url

    def _send_request(self, scope, method, endpoint, query=None):
        if query is None:
            query = {}

        # Build header first
        headers = self._build_headers(scope, method, endpoint, query)

        # Build final url here
        url = self._build_url(scope, method, endpoint, query)

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers).json()
            elif method == 'POST':
                response = requests.post(
                    url, headers=headers, json=query).json()
            elif method == 'DELETE':
                response = requests.delete(
                    url, headers=headers, json=query).json()
        except Exception as e:
            print('[x] Error: {}'.format(e.args[0]))

        if response['success'] is True:
            return response['data']
        else:
            return response

    # Public API
    def get_public_all_markets(self):
        """
        https://docs.dexlab.space/api-documentation/rest-api/pair-api

        :return: a list contains all available markets
        """

        return self._send_request('public', 'GET', f"pairs")

    def get_public_single_market(self, pair):
        """
        https://docs.dexlab.space/api-documentation/rest-api/pair-api

        :param pair: the trading pair to query (ex. BTC/USDT, SRM/SOL)
        :return: a list contains single market info
        """

        for info in self._send_request('public', 'GET', f"pairs"):
            if info['market'] == pair.upper():
                return info

        return f'[x] Error: the market {pair.upper()} is not exist'

    def get_public_orderbooks(self, market):
        """
        https://docs.dexlab.space/api-documentation/rest-api/orderbook-api


        :param market: the trading pair to query (Can be name or address. Ex. BTCUSDT, SRMSOL or EXnGBBSamqzd3uxEdRLUiYzjJkTwQyorAaFXdfteuGXe)
        :return: a dict contains asks and bids data
        """

        if len(market) < 15:
            return self._send_request('public', 'GET', f"orderbooks/{market}")
        else:
            return self._send_request('public', 'GET', f"orderbooks/address/{market}")

    def get_public_all_markets_price(self):
        """
        https://docs.dexlab.space/api-documentation/rest-api/price-api

        :return: a list contains the price of all available markets
        """

        return self._send_request('public', 'GET', f"prices")

    def get_public_single_market_price(self, market):
        """
        https://docs.dexlab.space/api-documentation/rest-api/price-api

        :param market: the trading pair to query (Can be name or address. Ex. BTC/USDT, SRM/SOL or EXnGBBSamqzd3uxEdRLUiYzjJkTwQyorAaFXdfteuGXe)
        :return: a dict contains the price info of market
        """

        if len(market) < 15:
            for info in self._send_request('public', 'GET', f"prices"):
                if info['market'] == market.upper():
                    return info
            return f'[x] Error: the market {market.upper()} is not exist'
        else:
            return self._send_request('public', 'GET', f"prices/{market}/last")

    def get_public_all_markets_price_change(self):
        """
        https://docs.dexlab.space/api-documentation/rest-api/price-api

        :return: a list contains the price-change of all available markets
        """

        return self._send_request('public', 'GET', f"prices/recent")

    def get_public_single_market_price_change(self, market):
        """
        https://docs.dexlab.space/api-documentation/rest-api/price-api

        :param market: the trading pair to query (Can be only address. Ex. EXnGBBSamqzd3uxEdRLUiYzjJkTwQyorAaFXdfteuGXe)
        :return: a dict contains the price-change of market
        """

        for info in self._send_request('public', 'GET', f"prices"):
            if info['market_address'] == market:
                return info
        return f'[x] Error: the market {market} is not exist'


    def get_public_single_market_yesterday_price(self, market):
        """
        https://docs.dexlab.space/api-documentation/rest-api/price-api

        :param market: the trading pair to query (Can be only address. Ex. EXnGBBSamqzd3uxEdRLUiYzjJkTwQyorAaFXdfteuGXe)
        :return: a dict contains the yesterday price of the market
        """

        return self._send_request('public', 'GET', f"prices/{market.upper()}/closing-price")

    def get_public_all_markets_volumes(self):
        """
        https://docs.dexlab.space/api-documentation/rest-api/volume-api

        :return: a list contains the volumes data of all available markets
        """

        return self._send_request('public', 'GET', f"volumes")

    def get_public_single_market_volumes(self, market):
        """
        https://docs.dexlab.space/api-documentation/rest-api/volume-api

        :param market: the trading pair to query (Can be name or address. Ex. BTC/USDT, SRM/SOL or EXnGBBSamqzd3uxEdRLUiYzjJkTwQyorAaFXdfteuGXe)
        :return: a dict contains the volumes data of market
        """

        if len(market) < 15:
            for info in self._send_request('public', 'GET', f"volumes"):
                if info['name'] == market.upper():
                    return info
            return f'[x] Error: the market {market.upper()} is not exist'
        else:
            return self._send_request('public', 'GET', f"volumes/{market}")

    def get_public_all_markets_volumes_total(self):
        """
        https://docs.dexlab.space/api-documentation/rest-api/volume-api

        :return: a dict contains the total volumes in USDT of market
        """

        return self._send_request('public', 'GET', f"volumes/summary/total-trade-price")

    def get_public_all_markets_trades(self):
        """
        https://docs.dexlab.space/api-documentation/rest-api/trade-api-1

        :return: a list contains the trades data of all available markets
        """

        return self._send_request('public', 'GET', f"trades")

    def get_public_single_market_trades(self, market):
        """
        https://docs.dexlab.space/api-documentation/rest-api/trade-api-1

        :param market: the trading pair to query (Can be only address. Ex. EXnGBBSamqzd3uxEdRLUiYzjJkTwQyorAaFXdfteuGXe)
        :return: a list contains the trades data of market
        """

        return self._send_request('public', 'GET', f"trades/{market}/all")

    def get_public_single_market_last_trade(self, market):
        """
        https://docs.dexlab.space/api-documentation/rest-api/trade-api-1

        :param market: the trading pair to query (Can be only address. Ex. EXnGBBSamqzd3uxEdRLUiYzjJkTwQyorAaFXdfteuGXe)
        :return: a list contains the last trade of market
        """

        return self._send_request('public', 'GET', f"trades/{market}/last")