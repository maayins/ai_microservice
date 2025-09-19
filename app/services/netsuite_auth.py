import hashlib
import hmac
import json
import requests
import base64
import time
import random
import urllib.parse

class NetSuiteAuth:

    def _generateTimestamp():
        return str(int(time.time()))

    def _generateNonce(length=11):
        """Generate pseudorandom number"""
        return ''.join([str(random.randint(0, 9)) for i in range(length)])

    def _generateSignature(method, url, consumerKey, Nonce, currentTime, token, consumerSecret,
                        tokenSecret, offset):
        signature_method = 'HMAC-SHA256'
        version = '1.0'
        base_url = url
        encoded_url = urllib.parse.quote_plus(base_url)
        collected_string = None
        if type(offset) == int:
            collected_string = '&'.join(['oauth_consumer_key=' + consumerKey, 'oauth_nonce=' + Nonce,
                                        'oauth_signature_method=' + signature_method, 'oauth_timestamp=' + currentTime,
                                        'oauth_token=' + token, 'oauth_version=' + version, 'offset=' + str(offset)])
        else:
            collected_string = '&'.join(['oauth_consumer_key=' + consumerKey, 'oauth_nonce=' + Nonce,
                                        'oauth_signature_method=' + signature_method, 'oauth_timestamp=' + currentTime,
                                        'oauth_token=' + token, 'oauth_version=' + version])
        encoded_string = urllib.parse.quote_plus(collected_string)
        base = '&'.join([method, encoded_url, encoded_string])
        key = '&'.join([consumerSecret, tokenSecret])
        digest = hmac.new(key=str.encode(key), msg=str.encode(base), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest).decode()
        return urllib.parse.quote_plus(signature)   
