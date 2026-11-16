from __future__ import annotations

import hashlib
import hmac
import json
import logging
from urllib.parse import parse_qsl

logger = logging.getLogger(__name__)


def parse_init_data(init_data: str) -> dict[str, str]:
    return {key: value for key, value in parse_qsl(init_data, keep_blank_values=True)}


def validate_init_data(init_data: str, bot_token: str) -> dict[str, str]:
    logger.info(f"Validating init_data (length={len(init_data)}, first 100 chars={init_data[:100]})")
    parsed = parse_init_data(init_data)
    logger.info(f"Parsed keys: {list(parsed.keys())}")
    
    received_hash = parsed.pop("hash", "")
    if not received_hash:
        logger.error("Hash is missing from init_data")
        raise ValueError("missing_hash")
    
    logger.info(f"Received hash: {received_hash[:20]}...")
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))
    logger.info(f"Data check string (first 100 chars): {data_check_string[:100]}")
    
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    logger.info(f"Computed hash: {computed_hash[:20]}...")
    
    if not hmac.compare_digest(computed_hash, received_hash):
        logger.error(f"Hash mismatch! Received: {received_hash[:20]}... vs Computed: {computed_hash[:20]}...")
        raise ValueError("invalid_hash")
    
    logger.info("Init data validation successful")
    return parsed


def extract_user_from_init_data(init_data: str, bot_token: str) -> dict:
    parsed = validate_init_data(init_data, bot_token)
    raw_user = parsed.get("user")
    if not raw_user:
        raise ValueError("missing_user")
    user = json.loads(raw_user)
    if not isinstance(user, dict) or "id" not in user:
        raise ValueError("invalid_user")
    return user
