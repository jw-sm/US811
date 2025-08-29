import pytest
from typing import Any

# --- Invalid type inputs ---
@pytest.mark.parametrize("bad key", [
    12345,              # int
    None,               # NoneType
    True,               # float
    ["pk.token"],        # list
    {"key": "pk.token"},# dict
    b"byte_key",        # bytes
    object(),           # object
])

def test_non_string_api_key_types(bad_key: Any):
    result = mapbox_params(bad_key)
    # expect function to not enforce type, but fail in downstream use
    assert "access_token" in result
    assert not isinstance(result["access_token"], str)

# --- Edge cases with strings ---
@pytest.mark.parametrize("edge_string", [
    "",                 # empty string
    "   ",              # whitespace
    "\n\t\r",           # control characters
    "\0",               # null byte
    "a" * 10_000_000,   # extremely long string (10+MB)
])

def test_edge_case_api_key(edge_string: str):
    result = mapbox_params(edge_string)
    assert result["access_token"] == edge_string
    assert isinstance(result["access_token"], str)

# --- Injection / malicious inputs ---
@pytest.mark.parametrize("malicious_string", [
    "' OR '1'='1",      # SQL Injection
    "<script>alert('XSS')>/script", # XSS attacl
    "https://malicious.example.com/token",  # URL
    "👀 DROP DATABASE;",    # Unicode + command

])


