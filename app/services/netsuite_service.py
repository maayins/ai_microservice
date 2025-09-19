import requests
import json
import random
import time
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from .netsuite_auth import NetSuiteAuth


def run_suite_ql_http_client(
    suite_ql_query:str,
    limit: Optional[str] = 1000,
    offset: Optional[str] = 0
) -> str:
    
    nsAccountID = "627386"
    consumerKey = "7d84f4f4c4cac7b7689facf5ab387bd896723ae7ce748bf5dbdb89e1f593fa55"
    consumerSecret = "8b58da4ec2daa13b3f41729321fdfa080f5685a94f6b8273f7091f9fae70cca0"
    token = "9026f8433cb32c15cb6bebd32f3e8115bc60522d7c12a257fbe4536e3bf5c511"
    tokenSecret = "093f4afc4111ba1016d7788a34ab56f6451be7476e1fd93d2d3009ec9867436b"
    base_url = "https://627386.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"
    Nonce = NetSuiteAuth._generateNonce(length=11)
    currentTime = NetSuiteAuth._generateTimestamp()

    signature = NetSuiteAuth._generateSignature('POST', base_url, consumerKey, Nonce, currentTime, token, consumerSecret, tokenSecret, offset)

    
    body = {
                "q": str(suite_ql_query)
            }   
    payload = json.dumps(body)    
    oauth = "OAuth realm=\"" + nsAccountID + "\"," \
            "oauth_consumer_key=\"" + consumerKey + "\"," \
            "oauth_token=\"" + token + "\"," \
            "oauth_signature_method=\"HMAC-SHA256\"," \
            "oauth_timestamp=\"" + currentTime + "\"," \
            "oauth_nonce=\"" + Nonce + "\"," \
            "oauth_version=\"1.0\"," \
            "oauth_signature=\"" + signature + "\""
    
    headers = {
        'prefer':'transient',
        'Content-Type': "application/json",
        'Authorization': oauth,
        'cache-control': "no-cache",
    }

    response = requests.request("POST", base_url + '?offset=' + str(offset), data=payload, headers=headers)
    try:
        return response.json()
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response", "raw": response.text}
#json.loads(response.text)