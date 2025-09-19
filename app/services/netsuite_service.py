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
    
    nsAccountID = "xxxx"
    consumerKey = "xxx"
    consumerSecret = "xxx"
    token = "xxx"
    tokenSecret = "xxx"
    base_url = "https://xxx.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"
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