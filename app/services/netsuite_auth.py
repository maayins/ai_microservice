import hashlib
import hmac
import base64
from urllib.parse import urlparse, parse_qs, quote
from collections import OrderedDict

class NetSuiteAuth:
    
    @staticmethod
    def generate_signature(http_method, url_string, ckey, csecret, tkey, tsecret,
                          timestamp, nonce, data=None):
        """
        Generate OAuth signature for NetSuite authentication
        
        Args:
            http_method (str): HTTP method (GET, POST, etc.)
            url_string (str): The full URL
            ckey (str): Consumer key
            csecret (str): Consumer secret
            tkey (str): Token key
            tsecret (str): Token secret
            timestamp (str): OAuth timestamp
            nonce (str): OAuth nonce
            data (dict): Additional data parameters (optional)
        
        Returns:
            str: The generated signature
        """
        
        if data is None:
            data = {}
        
        # Parse the URL to extract base endpoint and query parameters
        parsed_url = urlparse(url_string)
        original_endpoint = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        
        # Parse query parameters from URL
        query_parameters = parse_qs(parsed_url.query)
        
        # Create parameters dictionary (using OrderedDict to maintain order like SortedDictionary in C#)
        parameters = OrderedDict([
            ("oauth_consumer_key", ckey),
            ("oauth_token", tkey),
            ("oauth_signature_method", "HMAC-SHA256"),
            ("oauth_timestamp", timestamp),
            ("oauth_nonce", nonce),
            ("oauth_version", "1.0")
        ])
        
        # Add query parameters if they exist
        if query_parameters:
            for qkey, qvalue in query_parameters.items():
                # query parameters come as lists, take the first value
                parameters[qkey] = qvalue[0] if isinstance(qvalue, list) else qvalue
        
        # Handle additional data parameters (like the 'q' parameter logic in C#)
        for key, value in data.items():
            if key == "q":
                # This logic mirrors the C# code's special handling of 'q' parameter
                url_string = f"{url_string}?{key}={value}"
        
        # Sort parameters for signature generation
        sorted_parameters = OrderedDict(sorted(parameters.items()))
        
        # Build signature base string
        signature_base_string = http_method.upper() + "&"
        
        # Add percent-encoded URL
        percent_encoded_url = quote(original_endpoint, safe='')
        signature_base_string += percent_encoded_url + "&"
        
        # Add parameters
        first = True
        for key, value in sorted_parameters.items():
            if first:
                signature_base_string += quote(f"{key}={value}", safe='')
                first = False
            else:
                signature_base_string += quote(f"&{key}={value}", safe='')
        
        # Create signing key
        signing_key = f"{csecret}&{tsecret}"
        
        # Generate HMAC-SHA256 signature
        signature = base64.b64encode(
            hmac.new(
                signing_key.encode('ascii'),
                signature_base_string.encode('ascii'),
                hashlib.sha256
            ).digest()
        ).decode('ascii')
        
        # URL encode the signature
        encoded_signature = quote(signature, safe='')
        
        return encoded_signature
    
    @staticmethod
    def build_rest_auth(netsuite_account, ckey, tkey, signature_method,
                       timestamp, nonce, signature):
        """
        Build the OAuth authorization header string
        
        Args:
            netsuite_account (str): NetSuite account ID
            ckey (str): Consumer key
            tkey (str): Token key
            signature_method (str): Signature method (usually "HMAC-SHA256")
            timestamp (str): OAuth timestamp
            nonce (str): OAuth nonce
            signature (str): Generated signature
        
        Returns:
            str: Complete authorization header value
        """
        
        auth_header = (
            f'OAuth '
            f'realm="{netsuite_account}",'
            f'oauth_consumer_key="{ckey}",'
            f'oauth_token="{tkey}",'
            f'oauth_signature_method="{signature_method}",'
            f'oauth_timestamp="{timestamp}",'
            f'oauth_nonce="{nonce}",'
            f'oauth_version="1.0",'
            f'oauth_signature="{signature}"'
        )
        
        return auth_header


# Helper functions for generating OAuth parameters
import time
import random
import string

def generate_nonce(length=32):
    """Generate a random nonce"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_timestamp():
    """Generate current timestamp"""
    return str(int(time.time()))