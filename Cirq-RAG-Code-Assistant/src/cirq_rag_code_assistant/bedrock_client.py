"""
Bedrock client helper for Anthropic (and other Bedrock) model invocation.

Provides a shared bedrock-runtime client with region from config/env.
Credentials come from boto3's default chain (env vars, profile, etc.).
"""

import os
from typing import Any, Optional

try:
    import boto3
    from botocore.config import Config

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


def get_bedrock_runtime_client(
    region: Optional[str] = None,
    read_timeout: int = 300,
    connect_timeout: int = 10,
) -> Any:
    """
    Return a boto3 bedrock-runtime client.

    Region is taken from AWS_DEFAULT_REGION env, or config aws.region, or us-east-1.
    Credentials are not read from config; they come from env / .env / AWS profile only.
    """
    if not BOTO3_AVAILABLE:
        raise ImportError("boto3 is required for AWS Bedrock. Install it with: pip install boto3")
    if region is None:
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        if region == "us-east-1":
            try:
                from .config import get_config

                region = get_config().get("aws", {}).get("region", "us-east-1")
            except Exception:
                pass
    config = Config(
        read_timeout=read_timeout,
        connect_timeout=connect_timeout,
        retries={"max_attempts": 2, "mode": "standard"},
    )
    return boto3.client("bedrock-runtime", region_name=region, config=config)

