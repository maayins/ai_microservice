import requests
import json
import random
import time
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from netsuite_auth import NetSuiteAuth

@dataclass
class AppSettings:
    method: str
    endpoint: str
    signature_method: str

@dataclass
class DataSourceDto:
    account_id: str
    consumer_key: str
    consumer_secret: str
    token_key: str
    token_secret: str

def run_suite_ql_http_client(
    suite_ql_query: str,
    app_settings: AppSettings,
    auth: DataSourceDto,
    limit: Optional[str] = None,
    offset: Optional[str] = None
) -> str:
    """
    Executes a SuiteQL query against NetSuite's REST API
    
    Args:
        suite_ql_query: The SuiteQL query to execute
        app_settings: Application settings containing method and endpoint info
        auth: Authentication credentials for NetSuite
        limit: Optional limit for query results
        offset: Optional offset for query results
        
    Returns:
        JSON string containing the query results with column aliases
    """
    
    # Construct the base URL
    url_string = f"{app_settings.method}{auth.account_id}{app_settings.endpoint}query/v1/suiteql"
    
    # Build query parameters
    query_params = []
    if limit:
        query_params.append(f"limit={limit}")
    if offset:
        query_params.append(f"offset={offset}")
    
    # Append query parameters to URL if any exist
    if query_params:
        url_string += "?" + "&".join(query_params)
    
    # Prepare request body
    body = {"q": suite_ql_query}
    json_body = json.dumps(body)
    
    # Generate OAuth parameters
    timestamp = str(int(time.time()))
    nonce = str(random.randint(123400, 9999999))
    
    # Create data dictionary for signature generation (matching C# logic)
    query = ""
    data = {query if query != "" else "": query} if query else {}
    
    # Generate OAuth signature using your NetSuiteAuth class
    signature = NetSuiteAuth.generate_signature(
        "POST", url_string,
        auth.consumer_key, auth.consumer_secret,
        auth.token_key, auth.token_secret,
        timestamp, nonce, data
    )
    
    # Build authorization header using your NetSuiteAuth class
    net_suite_authorization = NetSuiteAuth.build_rest_auth(
        auth.account_id, auth.consumer_key,
        auth.token_key, app_settings.signature_method,
        timestamp, nonce, signature
    )
    
    # Get column aliases from SQL query
    aliases = get_aliases(suite_ql_query)
    
    # Make HTTP request
    headers = {
        "prefer": "transient",
        "Authorization": net_suite_authorization,
        "Content-Type": "application/json"
    }
    
    response = requests.post(url_string, data=json_body, headers=headers)
    response_content = response.text
    
    # Parse and modify response
    response_object = json.loads(response_content)
    response_object["columns"] = aliases
    
    # Return modified response
    return json.dumps(response_object)

def get_aliases(sql_query: str) -> List[str]:
    """
    Extract column aliases from SQL query
    
    Args:
        sql_query: The SQL query string
        
    Returns:
        List of column aliases found in the query
    """
    aliases = []
    
    # Clean up the query - replace newlines and carriage returns with spaces, then trim
    sql_query = sql_query.replace("\n", " ").replace("\r", " ").strip()
    
    # Updated regex to match aliases with double quotes, single quotes, backticks, or no quotes
    pattern = r'\s+AS\s+(?:["`\']([^"`\']+)["`\']|(\w+))'
    
    matches = re.finditer(pattern, sql_query, re.IGNORECASE)
    
    for match in matches:
        # Group 1 captures quoted aliases, Group 2 captures unquoted aliases
        alias = (match.group(1) if match.group(1) else match.group(2)).strip()
        aliases.append(alias)
    
    return aliases