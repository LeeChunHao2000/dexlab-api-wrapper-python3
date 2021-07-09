import hashlib
import hmac
import json
import requests
import urllib
from urllib.parse import quote_from_bytes, urlencode

from .constants import *
from .helpers import *

# The order API is still in preparation.
class Client(object):
    def __init__(self, key, timeout=30):
        self.key = key
        self._api_timeout = int(timeout)

    def _build_headers(self, scope, method, endpoint, query=None):

        headers = {
            'Accept': 'application/json',
            'User-Agent': 'DexLab-Trader/1.0',
        }

        if scope.lower() == 'private':
            headers.update({
                'x-wallet-private-key': self.key
            })

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
                print (url, headers, query)
                response = requests.post(
                    url, headers=headers, json=query).json()
            elif method == 'PUT':
                response = requests.put(
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

    # Private API (Read Only)

    def get_private_all_account_balances(self):
        """
        https://docs.dexlab.space/api-documentation/rest-api/beta-wallet-api-1

        :return: a list contains all account balances
        """

        return self._send_request('private', 'GET', f'wallet/balances')

    def get_private_open_orders(self, quote, base):
        """
        https://docs.dexlab.space/api-documentation/rest-api/order-api

        :param quote: the quote coin you trade
        :param base: the base coin you trade
        :return: a dict contains the open orders that have not yet been filled
        """

        query = {
            'coin': quote,
            'priceCurrency': base
        }

        return self._send_request('private', 'GET', f'orders/open-orders', query=query)

    def get_private_unsettle_balance(self, quote, base):
        """
        https://docs.dexlab.space/api-documentation/rest-api/order-api

        :param quote: the quote coin you settle
        :param base: the base coin you settle
        :return: a dict contains the balance that have not yet been settled
        """

        query = {
            'coin': quote,
            'priceCurrency': base
        }

        return self._send_request('private', 'GET', f'orders/settles', query=query)

    # Private API (Operation)
    def transfer_token(self, from, to, token, amount, cluster='mainnet'):
        """
        https://docs.dexlab.space/api-documentation/rest-api/wallet-api

        :param cluster: mainnet,devnet,testnet (default: mainnet)
        :param from: sending token address (BTC wallet address in case of BTC)
        :param to: recipient Wallet Address (SOL address if you have an outgoing token wallet)
        :param token: token contract address to send
        :param amount: quantity to send
        :return: a dict contains the operation result
        """

        query = {
            'from': from,
            'to': to,
            'tokenAddress': token,
            'amount': amount
        }

        return self._send_request('private', 'POST', f'wallet/transfer?cluster={cluster}', query=query)


    def settle_fund(self, quote, base):
        """
        https://docs.dexlab.space/api-documentation/rest-api/order-api

        :return: a dict contains the operation result
        """

        query = {
            'coin': quote,
            'priceCurrency': base
        }

        return self._send_request('private', 'POST', f'orders/settles', query=query)

    def place_order(self, side, quote, base, amount, price, type='limit'):
        """
        https://docs.dexlab.space/api-documentation/rest-api/order-api

        :param side: buy / sell
        :param quote: the quote coin you wanna trade
        :param base: the base coin you wanna trade
        :param amount: the quantity you wanna trade
        :param price: the price you wanna trade
        :param type: limit / ioc / postOnly (default: limit)
        :return: a dict contains the operation result and orderId
        """

        query = {
            'side': side,
            'coin': quote,
            'priceCurrency': base,
            'quantity': amount,
            'price': price,
            'orderType': type
        }

        return self._send_request('private', 'POST', f'orders', query=query)

    def cancel_order(self, orderId):
        """
        https://docs.dexlab.space/api-documentation/rest-api/order-api

        :param orderId: the order you wanna cancel
        :return: a dict contains the operation result
        """

        return self._send_request('private', 'PUT', f'orders/{orderId}/cancel')